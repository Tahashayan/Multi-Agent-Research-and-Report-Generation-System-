from app.agents.llm_setup import get_llm
from app.tools.web_search import web_search

tools = [web_search]

llm_with_tools = get_llm().bind_tools(tools)

system_prompt = "You are a helpful research assistant. Use the web search tool to find accurate information if you do not know the answer."

if __name__ == "__main__":
    response = llm_with_tools.invoke([
        ("system", system_prompt),
        ("human", "What is the latest stock price of Nvidia today?")
    ])

    print(response)