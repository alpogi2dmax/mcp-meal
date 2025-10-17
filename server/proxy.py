from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastmcp import Client

app = FastAPI()

MCP_HTTP_URL = "http://127.0.0.1:8000/mcp"  # Must include /mcp

class ProxyRequest(BaseModel):
    context: str

@app.post("/mcp/suggest")
async def suggest(req: ProxyRequest):
    try:
        async with Client(MCP_HTTP_URL) as client:
            # Use list_tools() if you need the tools
            # tools = await client.list_tools()
            
            # Call the tool
            res = await client.call_tool("suggest_meal", {"context": req.context})
            return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))