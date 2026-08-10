import json

from mcp import ClientSession

from mcp.client.streamable_http import streamable_http_client


class MCPClient:
    def __init__(self, url: str):
        self.url = url
        self._transport = None
        self.streams = None
        self.session: ClientSession | None = None

    async def connect(self):
        # streamable_http_client is an @asynccontextmanager; keep the transport
        # context open for the whole client lifetime (tools run inside it).
        self._transport = streamable_http_client(self.url)
        try:
            self.streams = await self._transport.__aenter__()
        except Exception:
            self._transport = None
            raise

        read_stream, write_stream = self.streams
        self.session = ClientSession(read_stream, write_stream)

        try:
            await self.session.__aenter__()
            await self.session.initialize()
        except BaseException as exc:
            for cm in (self.session, self._transport):
                if cm is None:
                    continue
                try:
                    await cm.__aexit__(type(exc), exc, exc.__traceback__)
                except BaseException:
                    pass
            self._transport = None
            self.session = None
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

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def list_tools(self):
        response = await self.session.list_tools()
        return [t.name for t in response.tools]

    async def call_tool(
        self, name: str, arguments: dict | None = None
    ) -> str:
        result = await self.session.call_tool(name, arguments or {})
        return self.format_result(result)

    @staticmethod
    def format_result(result) -> str:
        lines = []

        if getattr(result, "structuredContent", None):
            lines.append(
                json.dumps(result.structuredContent, indent=2, default=str)
            )

        for item in result.content:
            if hasattr(item, "text") and item.text:
                lines.append(str(item.text))

        return "\n".join(lines)