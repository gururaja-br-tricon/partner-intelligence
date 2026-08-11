import uvicorn

from app.mcp.server import mcp

if __name__ == "__main__":
    uvicorn.run(
        mcp.streamable_http_app(
            streamable_http_path="/mcp"
        ),
        host="0.0.0.0",
        port=8001,
    )