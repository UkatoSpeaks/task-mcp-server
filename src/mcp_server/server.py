from typing import Literal
from uuid import uuid4

from fastmcp import FastMCP

from mcp_server.database import (
    get_all_tasks,
    init_db,
    save_task,
    update_task_status_in_db,
)

mcp = FastMCP("Task Manager")


@mcp.tool
def create_task(
    title: str,
    priority: Literal["low", "medium", "high"] = "medium",
    description: str = "",
) -> dict:
    """Create a new task and save it. Returns the created task including its generated task_id."""
    task = {
        "task_id": str(uuid4()),
        "title": title,
        "description": description,
        "priority": priority,
        "status": "todo",
    }
    save_task(task)
    return task


@mcp.tool
def list_tasks() -> list[dict]:
    """List all saved tasks with their task_id, title, description, priority and status."""
    return get_all_tasks()


@mcp.tool
def update_task_status(
    task_id: str,
    status: Literal["todo", "in_progress", "done"],
) -> dict:
    """Change a task's status using its task_id. Use list_tasks first if you don't know the id."""
    return update_task_status_in_db(task_id, status)


if __name__ == "__main__":
    init_db()
    mcp.run(transport="http", host="127.0.0.1", port=8000)