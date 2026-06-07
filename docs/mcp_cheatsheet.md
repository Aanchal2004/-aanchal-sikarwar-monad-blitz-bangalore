# MCP (Model Context Protocol) Cheat Sheet

## What is MCP?

MCP lets AI agents connect to external tools/data sources through a standard protocol.
Think: plugins for LLMs — databases, APIs, file systems, blockchain nodes.

## Architecture

```
LLM Agent ←→ MCP Client ←→ MCP Server(s)
                              ├── filesystem
                              ├── github
                              ├── postgres
                              └── custom tools
```

## Use Cases for Hackathon

| MCP Server | Agent Use |
|------------|-----------|
| filesystem | Read/write project files |
| fetch | Web scraping for researcher agent |
| sqlite | Local task/reputation DB |
| custom-monad | Wallet balance, contract calls |

## Cursor MCP Config (example)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./datasets"]
    }
  }
}
```

## Custom MCP Server (Python sketch)

```python
# Simplified concept — use official MCP SDK
from mcp.server import Server

server = Server("monad-agent")

@server.tool()
async def get_balance(address: str) -> str:
    """Get MON balance on Monad testnet."""
    # call RPC
    return "1.25 MON"
```

## Integrate with LangChain

```python
# MCP tools can be wrapped as LangChain tools
from langchain_core.tools import StructuredTool

tool = StructuredTool.from_function(
    name="get_balance",
    func=get_balance,
    description="Get MON balance for address",
)
```

## Hackathon Strategy

- **Hour 1-4**: Skip MCP, use direct API calls
- **Hour 5-6**: Add MCP if you need filesystem or custom Monad tools
- **Demo**: Show agent reading from datasets/ via MCP

## Resources

- [MCP Spec](https://modelcontextprotocol.io)
- MCP servers: `@modelcontextprotocol/server-*` on npm
