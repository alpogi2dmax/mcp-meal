# MCP Meal — Meal Suggestion API via FastMCP + FastAPI

> **MCP Meal** is a lightweight project demonstrating how to use [FastMCP](https://pypi.org/project/fastmcp/) to build and expose AI/LLM-accessible microservices.  
> It connects to [TheMealDB](https://www.themealdb.com) API to suggest meal ideas based on ingredients you have on hand.

---

## Project Overview

This repository contains three key components:

```
mcp-meal/
├── server/
│ ├── fastmcp_server.py # Main FastMCP server hosting the meal suggestion tool
│ ├── proxy.py # FastAPI proxy server to expose MCP endpoint to external clients
│ ├── requirements.txt
│
└── client/
└── demo_client_fastmcp.py # Example async client demonstrating usage
```


## Features

- **FastMCP Integration** — defines a tool (`suggest_meal`) that LLMs or clients can call via MCP protocol.  
- **Smart Ingredient Parsing** — parses free-form text like “I have chicken, rice, and garlic.”  
- **Recipe Lookup** — fetches data from [TheMealDB API](https://www.themealdb.com/api.php).  
- **HTTP Proxy** — wraps the MCP service in a FastAPI endpoint for REST-style usage.  
- **Async Client Demo** — shows how to interact with the service programmatically.

---

## Tech Stack

| Component | Technology |
|------------|-------------|
| Core | [Python 3.9+](https://www.python.org/) |
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| MCP Runtime | [FastMCP ≥2.0](https://pypi.org/project/fastmcp/) |
| HTTP Client | `requests` |
| Server Runner | `uvicorn` |

---

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/alpogi2dmax/mcp-meal.git
cd mcp-meal/server

python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

pip install -r requirements.txt
```

## Running the Servers

This project runs two lightweight servers — one for FastMCP and one for FastAPI (proxy).

1. Start the FastMCP Server

```bash
cd server
python fastmcp_server.py
```

By default, it starts an MCP HTTP service at
http://127.0.0.1:8000/mcp

2. Start the FastAPI Proxy

This exposes a simple REST endpoint that forwards requests to the MCP server.

In a new terminal:

```bash
cd server
uvicorn proxy:app --reload --port 5000
```

The proxy will listen at:
http://127.0.0.1:5000/mcp/suggest

## Example Usage

### Using the REST API

Send a POST request to the Fast API proxy:

```bash
curl -X POST http://127.0.0.1:5000/mcp/suggest \
     -H "Content-Type: application/json" \
     -d '{"context": "I have chicken, rice, and onions"}'
```

**Example Response**:
```json

{
  "recipe": "Chicken Fried Rice",
  "category": "Main Course",
  "area": "Chinese",
  "instructions": "Heat oil, fry chicken pieces...",
  "youtube": "https://www.youtube.com/watch?v=abc123",
  "source": "https://www.themealdb.com/meal.php?i=52874",
  "matched_requested_ingredients": ["chicken", "rice", "onion"]
}

```

### Using the Demo Client

You can also run the async demo client that calls the MCP server directly:

```bash

cd client
python demo_client_fastmcp.py
```

Output example:
```rust

Tools: ['suggest_meal']
Result:
 {
   'recipe': 'Beef Stroganoff',
   'category': 'Beef',
   'area': 'Russian',
   'instructions': 'Slice beef thinly...',
   ...
 }

 ```

## Code Highlights

### The MCP Tool Definition (fastmcp_server.py)

```python

@mcp.tool()
def suggest_meal(context: str) -> Dict[str, Any]:
    """
    Suggest a meal based on free-text ingredient input.
    Example: "I have chicken, rice, and soy sauce"
    """
```

* Parses natural language ingredients lists.
* Queries TheMealDB API.
* Returns the most relevant recipe match.

### REST Proxy Design

proxy.py wraps the MCP server using FastAPI, providing a traditional REST API interface

```python

@app.post("/mcp/suggest")
async def suggest(req: ProxyRequest):
    async with Client(MCP_HTTP_URL) as client:
        res = await client.call_tool("suggest_meal", {"context": req.context})
        return res
```

### Dependencies

server/reqwuirements.txt

```shell

fastmcp>=2.0
requests>=2.28
fastapi>=0.95
uvicorn>=0.22
```

