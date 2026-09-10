import json
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from backend.app.agents.llm_setup import get_llm
from backend.app.tools.web_search import web_search
from backend.app.models.schemas import FinalReport
from backend.app.services.db_service import update_report_step
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
    validated = response if isinstance(response, FinalReport) else FinalReport.model_validate(response)
    return {"final_report": validated.model_dump()}
        

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
app = workflow.compile(checkpointer=memory, interrupt_after=["planner"])

def run_research_graph(report_id: str, topic: str):
    
    config = {"configurable": {"thread_id": report_id}}
    
    print(f"\n🚀 [STARTING] New research task started for: '{topic}'")
    inputs = {"messages": [HumanMessage(content=f"Research this topic: {topic}")]}
    
    update_report_step(report_id, "Planner is thinking...")
    
    for output in app.stream(inputs, config):
        pass
    
    final_state = app.get_state(config)
    print("\n🧠 [MEMORY CHECK] Here is the saved state in LangGraph:")
    print(final_state.values.keys())
    print(f"⏸️  [PAUSED] Next node: {final_state.next}")
    
    if final_state.next and "researcher" in final_state.next:
        print(f"🛑 [AWAITING APPROVAL] Research plan ready for '{topic}', waiting for user approval.\n")
        return "pending_approval"
                
    print(f"🏁 [FINISHED] Research complete for: '{topic}'\n")
    
    return None



def resume_research_graph(report_id: str):
    config = {"configurable": {"thread_id": report_id}}
    print(f"\n▶️  [RESUMING] Continuing research task for report_id: '{report_id}'")
    
    final_report = None
    
    for output in app.stream(None, config):
        for node_name, state_update in output.items():
            print(f"✅ [AGENT UPDATE] '{node_name.upper()}' just finished its task.")
            
            if node_name == "researcher":
                update_report_step(report_id, "Searcher the web...")
            elif node_name == "writer":
                update_report_step(report_id, "Drafting the final report...")
            
            if node_name == "writer":
                final_report = state_update["final_report"]
    
    print(f"🏁 [FINISHED] Research complete for report_id: '{report_id}'\n")
    
    if hasattr(final_report, "model_dump"):
        final_report_dict = final_report.model_dump()
    else:
        final_report_dict = json.loads(json.dumps(final_report, default=str))
    
    del final_report
    del output
    del node_name
    del state_update
    
    return final_report_dict
