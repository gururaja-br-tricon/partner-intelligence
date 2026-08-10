import os

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()


class MCPClient:

    def __init__(self, server_url=None):
        self.server_url = server_url or os.getenv(
            "MCP_SERVER_URL",
            "http://127.0.0.1:8001/mcp",
        )

        self._http_client = None
        self._session = None

    async def connect(self):
        self._http_client = streamable_http_client(self.server_url)

        read_stream, write_stream = await self._http_client.__aenter__()

        self._session = ClientSession(
            read_stream,
            write_stream,
        )

        await self._session.__aenter__()
        await self._session.initialize()

    async def disconnect(self):
        if self._session:
            await self._session.__aexit__(None, None, None)
            self._session = None

        if self._http_client:
            await self._http_client.__aexit__(None, None, None)
            self._http_client = None

    async def list_tools(self):
        if not self._session:
            raise RuntimeError("MCP client is not connected")

        result = await self._session.list_tools()

        return result.tools

    async def call_tool(self, tool_name, arguments=None):
        if not self._session:
            raise RuntimeError("MCP client is not connected")

        result = await self._session.call_tool(
            tool_name,
            arguments or {},
        )

        return result
