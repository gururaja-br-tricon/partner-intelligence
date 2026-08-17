import asyncio

from app.mcp_server.server import mcp


async def main():
    result = await mcp.call_tool("get_partner_profile", {"partner_id": "P001"})

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
