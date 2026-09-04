from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from app.agents.llm_setup import get_llm
from app.tools.web_search import web_search
from app.models.schemas import FinalReport
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

llm_with_tools = get_llm().bind_tools([web_search])

tool_node = ToolNode([web_search])

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    research_plan: str
    final_report: FinalReport

def planner_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"research_plan": response.content}

def research_node(state: AgentState):
    research_plan = state["research_plan"]
    response = llm_with_tools.invoke(research_plan)
    return {"final_report": response.content}

def writer_node(state: AgentState):
    structured_llm = llm_with_tools.with_structured_output(FinalReport)
    response = structured_llm.invoke(state["messages"])
    return {"final_report": response}
        

workflow = StateGraph(AgentState)


workflow.add_node("planner", planner_node)
workflow.add_node("researcher", research_node)
workflow.add_node("tools", tool_node)
workflow.add_node("writer", writer_node)
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_conditional_edges(
    "researcher",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "writer",
    }
)
workflow.add_edge("tools", "researcher")
workflow.add_edge("writer", END)

app = workflow.compile()

if __name__ == "__main__":
    inputs = {"messages": [HumanMessage(content="Analyze the current market difference between Apple Vision Pro and Meta Quest 3.")]}
    
    result = app.invoke(inputs)
    
    print(result["final_report"])
