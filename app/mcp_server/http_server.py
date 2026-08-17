import uvicorn

from app.mcp_server.server import mcp

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    print("Server starting at: http://{host}:{port}")
    uvicorn.run(mcp.streamable_http_app(streamable_http_path="/mcp"), host=host, port=port)
    print("Server started at: http://{host}:{port}")
