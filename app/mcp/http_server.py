import uvicorn
from fastapi import FastAPI

from app.mcp.server import mcp


app = FastAPI()

mcp_app = mcp.streamable_http_app()

app.mount("/mcp", mcp_app)


@app.get("/tools")
async def list_tools():
    tools = await mcp.list_tools()

    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in tools
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)