# Model Context Protocol (MCP)

## TL;DR
The Model Context Protocol (MCP) is an open standard that standardizes how AI models connect to data sources and tools. Instead of hardcoding API integrations for every new tool, MCP allows agents to dynamically discover and use tools provided by external, standardized MCP servers.

---

## What is MCP?
Historically, if you wanted your agent to talk to Slack, Jira, and GitHub, you had to write custom Python wrappers for the Slack API, Jira API, and GitHub API, convert them to JSON schemas, and manually pass them to the LLM.

MCP standardizes this. It is a client-server architecture where:
- **MCP Hosts (Clients):** The AI Agent, IDE (like Cursor), or application interface.
- **MCP Clients (Protocol layer):** The connection layer that manages communication.
- **MCP Servers:** Lightweight programs that expose specific capabilities (like a SQLite database, a GitHub repo, or a local file system) via a standard interface.

## Why it Standardizes Tool Interfaces
MCP defines a universal format for:
1. **Resources:** Read-only data (e.g., a file, an API response).
2. **Prompts:** Pre-defined templates for interactions.
3. **Tools:** Executable functions (e.g., executing a query, committing code).

By adhering to MCP, any agent framework (LangChain, LlamaIndex, custom loops) can instantly connect to any MCP Server without custom integration code.

## Dynamic Tool Discovery
Instead of a hardcoded tool list in your system prompt, an MCP-enabled agent queries the connected MCP Servers at runtime: "What tools do you have?"
The server responds with the schemas. This allows you to hot-swap capabilities. If a user connects their personal Google Drive MCP server to the agent, the agent instantly gains the ability to search Drive, without deploying new code.

## Hardcoded Lists vs MCP
- **Hardcoded:** `tools = [search_web_tool, calculate_tool, get_weather_tool]` -> Tightly coupled, requires application deployment to update, hard to share across different agent projects.
- **MCP:** Agent connects to `weather-mcp-server`. The server defines the schema and handles execution. -> Loosely coupled, reusable across any MCP-compliant AI application.

## Production Implications
MCP is designed with security in mind. Because MCP servers run locally or in isolated environments, they define the boundaries of what the agent can do. If you want an agent to read your local codebase, you run a local filesystem MCP server. The agent only gets access to the directories that the server explicitly exposes, preventing the AI from wandering into sensitive system files.

## Common Mistakes
- **Confusing MCP with an Agent Framework:** MCP is not a replacement for LangGraph or AutoGen; it is a replacement for custom tool wrappers. The framework still handles the reasoning loop.
- **Over-exposing Resources:** Pointing a filesystem MCP server at the root directory `/` instead of isolating it to a specific project workspace.

## Interview Questions
- **Q: What problem does the Model Context Protocol (MCP) solve?**
  - A: It eliminates the need to write custom integration code for every tool and data source by providing a standardized client-server protocol for AI agents to discover and interact with external systems.
- **Q: How does tool discovery work in MCP?**
  - A: The agent (host) connects to an MCP server and requests a list of available tools. The server returns the standardized schemas, which the agent can then pass to the LLM.

## Further Reading
- [Model Context Protocol Specification](https://modelcontextprotocol.io/) — The official documentation for MCP.
