# src/mcp_project/client.py
import os, sys, json, asyncio
from mcp.types import TextContent

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

SERVER_CMD  = sys.executable                       # use current python
SERVER_ARGS = ["-m", "mcp_project.agents.key_officers_agent"]
ENV = dict(os.environ, LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"), PYTHONUNBUFFERED="1")

async def main(company_name="Acme Ltd", top_n=5):
    # New API first, fall back to old
    try:
        from mcp.client.stdio import stdio_client, StdioServerParameters
        params = StdioServerParameters(command=SERVER_CMD, args=SERVER_ARGS, env=ENV, cwd=PROJECT_ROOT)
        start_ctx = stdio_client(params)
    except ImportError:
        from mcp.client.stdio import StdioServerParameters, connect_stdio_server
        params = StdioServerParameters(command=SERVER_CMD, args=SERVER_ARGS, env=ENV, cwd=PROJECT_ROOT)
        start_ctx = connect_stdio_server(params)

    async with start_ctx as (read, write):
        from mcp.client.session import ClientSession
        try:
            # Give the handshake a timeout so we fail fast if the server crashes at start
            session = await asyncio.wait_for(ClientSession.create(read, write), timeout=10)
        except AttributeError:
            session = ClientSession(read, write)
            await asyncio.wait_for(session.initialize(), timeout=10)

        tools = await session.list_tools()
        print("TOOLS:", [t.name for t in tools.tools])

        res = await session.call_tool("get_key_officers", {"company_name": company_name, "top_n": top_n})
        out = []
        for c in res.content:
            if isinstance(c, TextContent):
                out.append(c.text)
            else:
                out.append(c.model_dump() if hasattr(c, "model_dump") else c)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        await session.close()

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "Acme Ltd"
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    asyncio.run(main(company, top_n))
