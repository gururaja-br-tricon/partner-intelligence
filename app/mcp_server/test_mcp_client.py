import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as streams:

        read_stream, write_stream = streams

        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("\n--- Available Tools ---")

            for tool in tools.tools:
                print(tool.name)

            print("\n--- Calling search_partners ---")

            result = await session.call_tool(
                "search_partners",
                {
                    "headquarters_state": "Texas",
                    "vendor": "Microsoft",
                    "partner_tier": "Gold",
                    "capability": "AI",
                    "proficiency_level": "Expert",
                },
            )

            print("\n--- Result ---")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
