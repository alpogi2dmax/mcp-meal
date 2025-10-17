import asyncio
from fastmcp import Client

MCP_URL = "http://127.0.0.1:8000/mcp"

async def main():
    async with Client(MCP_URL) as client:
        tools = await client.list_tools()  # ✅ await here
        print("Tools:", tools)

        ctx = "I have beef, cream, and onions"
        result = await client.call_tool("suggest_meal", {"context": ctx})
        print("Result:\n", result.structured_content)  # easier to read

if __name__ == "__main__":
    asyncio.run(main())