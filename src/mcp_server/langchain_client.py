import asyncio
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

client = MultiServerMCPClient(
    {
        "tasks": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        }
    }
)

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


async def main():
    tools = await client.get_tools()
    print("Loaded tools:", [t.name for t in tools])

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a helpful task management assistant. "
            "Use the available tools to create, list and update tasks. "
            "If you need a task_id, call list_tasks first instead of asking the user."
        ),
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": str(uuid4())}}
    human_question = "Can you help me?"

    while human_question.strip().lower() != "q":
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=human_question)]},
            config=config,
        )
        print("\nAgent:", result["messages"][-1].text, "\n")
        human_question = input("You (q to exit): ")


if __name__ == "__main__":
    asyncio.run(main())