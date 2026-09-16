import asyncio
import os

from dotenv import load_dotenv
from google import genai

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

server_params = StdioServerParameters(
    command = "python",
    args = ["server.py"]
)

async def main():
    "start MCP server and connect it"
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_result = await session.list_tools()

            print("\nMCP Tools:")
            for tool in tool_result.tools:
                print(f"{tool.name}: {tool.description}")

            gemini_tools = []

            for tool in tool_result.tools:
                gemini_tools.append(
                    {
                        "type":"function",
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema
                    }
                )

            user_prompt = input("\nAsk Something: ")

            interaction  = gemini.interactions.create(
                model = "gemini-2.5-flash-lite",
                input = user_prompt,
                tools = gemini_tools,
            )

            for step in interaction.steps:
                if step.type == "function_call":
                    print(f"\nGemini wants to call: "
                          f"{step.name} ({step.arguments})")

                    result = await session.call_tool(
                        step.name,
                        arguments = step.arguments,
                    )

                    output = []

                    for content in result.content:
                        if hasattr(content, "text"):
                            output.append(content.text)

                    tool_result = "\n".join(output)

                    print(f"MCP returned: {tool_result}")

                    interaction = gemini.interactions.create(
                        model = "gemini-2.5-flash-lite",
                        previous_interaction_id=interaction.id,
                        input = [
                            {
                                "type":"function_result",
                                "name": step.name,
                                "call_id": step.id,
                                "result": tool_result,
                            }
                        ],
                    )
            print("\nGemini:")
            print(interaction.output_text)


if __name__ == "__main__":
    asyncio.run(main())