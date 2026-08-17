import json

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPClient:
    def __init__(self, url: str, auth_token: str | None = None):
        self.url = url
        self.auth_token = auth_token
        self._transport = None
        self._http_client = None
        self.streams = None
        self.session: ClientSession | None = None

    async def connect(self):
        # Build our own httpx client carrying the JWT, since
        # streamable_http_client doesn't take headers directly — it wants
        # the auth already baked into the http_client passed to it.
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        self._http_client = httpx2.AsyncClient(headers=headers)

        self._transport = streamable_http_client(
            self.url, http_client=self._http_client
        )
        try:
            self.streams = await self._transport.__aenter__()
        except Exception:
            self._transport = None
            await self._http_client.aclose()
            self._http_client = None
            raise

        read_stream, write_stream = self.streams
        self.session = ClientSession(read_stream, write_stream)

        try:
            await self.session.__aenter__()
            await self.session.initialize()
        except BaseException as exc:
            import traceback

            print("MCPClient connect failed — underlying exception:")
            traceback.print_exception(type(exc), exc, exc.__traceback__)
            for cm in (self.session, self._transport):
                if cm is None:
                    continue
                try:
                    await cm.__aexit__(type(exc), exc, exc.__traceback__)
                except BaseException:
                    pass
            self._transport = None
            self.session = None
            if self._http_client is not None:
                await self._http_client.aclose()
                self._http_client = None
            raise ConnectionError(
                f"Failed to connect to MCP server at {self.url}: {exc}"
            ) from exc

        return self

    async def close(self):
        if self.session is not None:
            await self.session.__aexit__(None, None, None)
            self.session = None
        if self._transport is not None:
            await self._transport.__aexit__(None, None, None)
            self._transport = None
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def list_tools(self):
        response = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.input_schema,
            }
            for tool in response.tools
        ]

    async def call_tool(self, name: str, arguments: dict | None = None) -> str:
        result = await self.session.call_tool(name, arguments or {})
        return self.format_result(result)

    @staticmethod
    def format_result(result) -> str:
        lines = []
        if getattr(result, "structuredContent", None):
            lines.append(json.dumps(result.structuredContent, indent=2, default=str))
        for item in result.content:
            if hasattr(item, "text") and item.text:
                lines.append(str(item.text))
        return "\n".join(lines)

    @staticmethod
    def to_llm_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in tools
        ]
