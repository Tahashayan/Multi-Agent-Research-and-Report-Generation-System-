from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from backend.app.agents.llm_setup import get_llm
from backend.app.tools.web_search import web_search
from backend.app.models.schemas import FinalReport
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

llm_with_tools = get_llm().bind_tools([web_search])

tool_node = ToolNode([web_search])

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    research_plan: str
    final_report: dict

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
    return {"final_report": response.model_dump()}
        

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

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def run_research_graph(report_id: str, topic: str):
    
    config = {"configurable": {"thread_id": report_id}}
    
    print(f"\n🚀 [STARTING] New research task started for: '{topic}'")
    inputs = {"messages": [HumanMessage(content=f"Research this topic: {topic}")]}
    
    final_report = None
    
    # app.stream yields the output after EVERY single node finishes
    for output in app.stream(inputs, config):
        # 'output' is a dictionary: {"node_name": {"state_key": "state_value"}}
        for node_name, state_update in output.items():
            print(f"✅ [AGENT UPDATE] '{node_name.upper()}' just finished its task.")
            
            # If the node that just finished was the writer, grab the report!
            if node_name == "writer":
                final_report = state_update["final_report"]
                
    print(f"🏁 [FINISHED] Research complete for: '{topic}'\n")
    
    final_state = app.get_state(config)
    print("\n🧠 [MEMORY CHECK] Here is the saved state in LangGraph:")
    print(final_state.values.keys())
    
    return final_report

