import asyncio
from fastmcp import Client

MCP_URL = "http://127.0.0.1:8000"  # match your server host/port

async def main():
    async with Client(MCP_URL) as client:
        print("Available tools:", list(client.tools.keys()))
        # Test the suggest_meal tool
        result = await client.call_tool("suggest_meal", {"context": "I have chicken, rice, tomato"})
        print(result)

asyncio.run(main())