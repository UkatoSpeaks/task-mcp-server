# MCP Task Manager

A small task manager exposed as an [MCP](https://modelcontextprotocol.io) server. It is built with
[FastMCP](https://gofastmcp.com) and stores tasks in SQLite. Any MCP client can create, list and update
tasks over HTTP: Claude Code, Codex, the included Python client, or the included LangChain agent.

## Architecture

```
 Claude Code ─┐
 Codex ───────┤   streamable HTTP    ┌──────────────────────┐      ┌──────────────────┐
 client.py ───┼────────────────────▶ │  server.py (FastMCP) │ ───▶ │  database.py     │
 LangChain ───┘ http://127.0.0.1:    │  3 tools             │      │  SQLite          │
 agent           8000/mcp            └──────────────────────┘      │  data/task.db    │
                                                                    └──────────────────┘
```

| Component | File | Role |
|---|---|---|
| Server | `src/mcp_server/server.py` | FastMCP server that registers the tools, creates the database on start (`init_db()`) and serves on `http://127.0.0.1:8000/mcp` |
| Database | `src/mcp_server/database.py` | SQLite layer: `init_db`, `save_task`, `get_all_tasks`, `update_task_status_in_db`. The database file is `data/task.db` at the project root and is created automatically |
| Python client | `src/mcp_server/client.py` | Minimal FastMCP client. It lists the tools, creates a task and prints all tasks |
| LangChain agent | `src/mcp_server/langchain_client.py` | Interactive chat agent (Groq `openai/gpt-oss-120b`) that uses the MCP tools through `langchain-mcp-adapters` |
| Claude Code / Codex | n/a | Connect to the same HTTP endpoint as MCP servers (see below) |

## Tools

| Tool | Parameters | Returns |
|---|---|---|
| `create_task` | `title` (str, required)<br>`priority`: `low` \| `medium` \| `high` (default `medium`)<br>`description` (str, default `""`) | The created task. `task_id` is a generated UUID and `status` is always `todo` |
| `list_tasks` | none | A list of all tasks |
| `update_task_status` | `task_id` (str, required)<br>`status`: `todo` \| `in_progress` \| `done` | The updated task, or `{"error": "Task with id ... does not exist"}` if the id is unknown |

Every task has these fields: `task_id`, `title`, `description`, `priority`, `status`. Invalid `priority` or `status`
values are rejected by the server's input validation.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer.

```bash
uv sync
```

The LangChain agent also needs a Groq API key:

```bash
cp .env.example .env
# then edit .env and set GROQ_API_KEY=...
```

`.env`, `.venv/`, `data/` and `*.db` are git-ignored.

## Running

Start the server first and leave it running in its own terminal. The other parts all connect to it.

```bash
uv run python -m mcp_server.server         # MCP server on http://127.0.0.1:8000/mcp
```

Then, in another terminal:

```bash
uv run python -m mcp_server.client           # Python client: list tools, create a task, list tasks
uv run python -m mcp_server.langchain_client # LangChain agent chat (type q to exit)
```

Tasks persist in `data/task.db` across server restarts. To start over, stop the server and delete that file.

## Connecting to Claude Code

With the server running:

```bash
claude mcp add --transport http tasks http://127.0.0.1:8000/mcp
claude mcp list     # "tasks" should show as connected
```

Inside Claude Code you can then ask things like "create a high priority task to write tests" or
"mark the tests task as done". Run `/mcp` in a session to check the server's status.

## Connecting to Codex

Add the server to `~/.codex/config.toml`:

```toml
[mcp_servers.tasks]
url = "http://127.0.0.1:8000/mcp"
```

Recent Codex CLI versions can also add it from the command line:

```bash
codex mcp add tasks --url http://127.0.0.1:8000/mcp
```

Run `/mcp` inside Codex to confirm that the three tools are listed. Older Codex versions only support
stdio MCP servers. If HTTP servers don't show up, update Codex.

## Project layout

```
.
├── pyproject.toml
├── .env.example
├── data/task.db            # created at runtime (git-ignored)
└── src/mcp_server/
    ├── server.py
    ├── database.py
    ├── client.py
    └── langchain_client.py
```
