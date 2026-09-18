import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai

from mcp import Client, StdioServerParameters


load_dotenv()

gemini = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


server_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "server.server"],
    errlog=sys.stderr,
)

def extract_tool_result(result) -> str:
    """Convert an MCP tool result into clean text."""

    texts = []

    for content in result.content:
        if hasattr(content, "text"):
            texts.append(content.text)

    if result.is_error:
        return "\n".join(texts) or "Tool execution failed."

    if result.structured_content is not None:
        return str(result.structured_content)

    return "\n".join(texts) or "Tool returned no content."

async def call_mcp_tool(client, tool_name, arguments, retries=2):

    for attempt in range(retries + 1):

        try:
            result = await client.call_tool(
                tool_name,
                arguments,
            )

            if not result.is_error:
                return result

            error_text = extract_tool_result(result)

            # Never retry authorization-sensitive tools
            if tool_name in {
                "get_order_tool",
                "search_orders_tool",
                "refund_order_tool",
                "get_customer_tool",
                "create_support_ticket_tool",
            }:
                return result

            if attempt < retries:

                print(
                    f"Tool failed. "
                    f"Retrying ({attempt + 1}/{retries})..."
                )

                await asyncio.sleep(1)
                continue

            return result

        except Exception as error:

            if attempt < retries:

                print(
                    f"Tool exception: {error}. "
                    f"Retrying ({attempt + 1}/{retries})..."
                )

                await asyncio.sleep(1)

            else:
                raise

async def main():

    async with Client(server_params) as client:

        print(f"\nMCP Server: {client.server_info.name}")
        print(f"Protocol: {client.protocol_version}")

        # Discover MCP tools
        tools_result = await client.list_tools()
        resources_result = await client.list_resources()

        print("\nMCP Resources:")

        for resource in resources_result.resources:
            print(f"{resource.uri}: {resource.name}")

        print("\nMCP Tools:")

        for tool in tools_result.tools:
            print(f"{tool.name}: {tool.description}")

        # Convert MCP tools to Gemini tools
        gemini_tools = []

        for tool in tools_result.tools:
            gemini_tools.append(
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                }
            )

        user_prompt = input("\nAsk Something: ")
        policy = await client.read_resource("policy://refund")

        policy_text = ""

        for content in policy.contents:
            if hasattr(content, "text"):
                policy_text += content.text

        user_prompt = f"""
        You are an e-commerce customer support agent.

        Company refund policy:
        {policy_text}

        Customer request:
        {user_prompt}

        Before requesting a refund:
        1. Check the order.
        2. Evaluate the order against the refund policy.
        3. Only request a refund if the order appears eligible.
        """

        # First Gemini request
        interaction = gemini.interactions.create(
            model="gemini-3.5-flash-lite",
            input=user_prompt,
            tools=gemini_tools,
        )

        # Process Gemini tool calls
        while True:

            function_calls = [
                step
                for step in interaction.steps
                if step.type == "function_call"
            ]

            if not function_calls:
                break

            function_results = []

            for step in function_calls:

                print(
                    f"\nGemini wants to call: "
                    f"{step.name} ({step.arguments})"
                )

                # -----------------------------
                # Human approval for write tools
                # -----------------------------

                write_tools = {
                    "refund_order_tool",
                    "create_support_ticket_tool"
                }

                if step.name in write_tools:

                    print("\n⚠️ Approval required")
                    print(f"Action: {step.name}")
                    print(f"Arguments: {step.arguments}")

                    approval = (
                        input("Approve this action? (yes/no): ")
                        .strip()
                        .lower()
                    )

                    if approval != "yes":

                        tool_result = {
                            "success": False,
                            "error": "Action rejected by human operator."
                        }

                        print("\nAction rejected.")

                    else:

                        result = await call_mcp_tool(
                            client,
                            step.name,
                            step.arguments,
                        )

                        tool_result = extract_tool_result(result)

                        print("\nAction approved.")
                        print(f"MCP returned: {tool_result}")

                # -----------------------------
                # Read-only tools
                # -----------------------------

                else:

                    result = await call_mcp_tool(
                        client,
                        step.name,
                        step.arguments,
                    )

                    tool_result = extract_tool_result(result)

                    print(f"\nMCP returned: {tool_result}")

                # -----------------------------
                # Prepare result for Gemini
                # -----------------------------

                function_results.append(
                    {
                        "type": "function_result",
                        "name": step.name,
                        "call_id": step.id,
                        "result": [
                            {
                                "type": "text",
                                "text": str(tool_result),
                            }
                        ],
                    }
                )

            # Send ALL tool results back to Gemini
            interaction = gemini.interactions.create(
                model="gemini-3.5-flash-lite",
                previous_interaction_id=interaction.id,
                input=function_results,
                tools=gemini_tools,
            )

        print("\nGemini:")
        print(interaction.output_text)


if __name__ == "__main__":
    asyncio.run(main())