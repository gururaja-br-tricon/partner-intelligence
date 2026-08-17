import uvicorn
from mcp.server.transport_security import TransportSecuritySettings

from app.mcp_server.server import mcp

if __name__ == "__main__":
    host = "0.0.0.0"  # 127.0.0.1 is unreachable from outside the container
    port = 8000
    print(f"Server starting at: http://{host}:{port}")
    uvicorn.run(
        mcp.streamable_http_app(
            streamable_http_path="/mcp",
            transport_security=TransportSecuritySettings(
                # SDK's default only allowlists 127.0.0.1/localhost/::1 —
                # Docker's service-name networking sends Host: mcp-server:8000,
                # which the default rejects with 421 Misdirected Request.
                # This is DNS-rebinding protection, not disabled outright —
                # just extended to the real hostnames this server is
                # reachable at (local dev + Docker Compose service name).
                allowed_hosts=[
                    "127.0.0.1:8000",
                    "localhost:8000",
                    "mcp-server:8000",
                ],
            ),
        ),
        host=host,
        port=port,
    )
