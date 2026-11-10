from typing import Literal
from uuid import uuid4

from fastmcp import FastMCP
from mcp_server.database import(
    get_all_tasks,
    save_task,
    update_task_status_in_db
)



mcp=FastMCP("MCP SERVER")


@mcp.tool(name="create_task",  description="this tool is created to create new tasks")
def create_task(title:str,priority:str="medium",description:str="")->dict:
    """
    this function creates new tasks in our database
    """

    task_id=str(uuid4())
    status="to do"

    task={"task_id":task_id, "title":title, "description":description, "status":status , "priority":priority}

    save_task(task)



@mcp.tool()
@mcp.tool()