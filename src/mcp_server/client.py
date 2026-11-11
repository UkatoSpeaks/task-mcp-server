import asyncio

from fastmcp import Client

client = Client("http://127.0.0.1:8000/mcp")


async def main():
    async with client:
        tools = await client.list_tools()
        print("Tools:", [t.name for t in tools])

        result = await client.call_tool(
            "create_task",
            {
                "title": "task3",
                "priority": "high",
                "description": "this is a test from our client",
            },
        )
        print("Created:", result.data)

        all_tasks = await client.call_tool("list_tasks", {})
        print("All tasks:", all_tasks.data)


if __name__ == "__main__":
    asyncio.run(main())