import asyncio

from app.mcp_server.client import MCPClient


async def main():
    client = MCPClient()

    try:
        await client.connect()

        tools = await client.list_tools()

        print("=" * 60)
        print("AVAILABLE MCP TOOLS")
        print("=" * 60)

        for tool in tools:
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Schema: {tool.input_schema}")
            print("-" * 60)

        print("=" * 60)
        print("CALLING search_partners")
        print("=" * 60)

        result = await client.call_tool(
            "search_partners",
            {
                "capability": "Cybersecurity"
            },
        )

        print(result)

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())