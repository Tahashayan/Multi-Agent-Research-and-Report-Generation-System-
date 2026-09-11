import json
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from backend.app.agents.llm_setup import get_llm
from backend.app.tools.web_search import web_search
from langchain_core.messages import SystemMessage 
from backend.app.models.schemas import FinalReport
from backend.app.services.db_service import update_report_step, update_report_content
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
    # 1. Get the topic
    topic_message = state["messages"][0].content
    
    # 2. Use a strict System Prompt to FORCE the local LLM to output text
    messages = [
        SystemMessage(content="You are an expert research planner. You must write a 3-step web search plan. You MUST respond with plain text. Do not leave your response blank."),
        HumanMessage(content=f"Create a 3-step research plan for this topic: {topic_message}")
    ]
    
    # 3. Call the LLM (without tools)
    response = get_llm().invoke(messages)
    plan_text = response.content
    
    # 4. THE FAILSAFE: If the local model still returns a blank string, inject a default plan!
    if not plan_text or str(plan_text).strip() == "":
        print("⚠️ [WARNING] The LLM returned a blank plan. Using failsafe plan.")
        plan_text = (
            f"1. Search the web for the latest news and updates regarding '{topic_message}'.\n"
            f"2. Analyze the technical specifications, pricing, and market reception.\n"
            f"3. Compare the findings with top competitors in the industry."
        )
        
    return {"research_plan": plan_text}

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
    
    # This works now because it was imported at the very top of the file!
    update_report_step(report_id, "Planner is thinking...")
    
    for output in app.stream(inputs, config):
        pass
    
    final_state = app.get_state(config)
    print("\n🧠 [MEMORY CHECK] Here is the saved state in LangGraph:")
    print(final_state.values.keys())
    print(f"⏸️  [PAUSED] Next node: {final_state.next}")
    
    current_state = app.get_state(config)
    next_node = current_state.next
    
    if "researcher" in next_node:
        print("\n✋ [PAUSED] The graph is waiting for human approval!")
        plan = current_state.values.get("research_plan", "No plan found")
        
        # We removed the import from here. Just call the functions directly!
        update_report_step(report_id, "Waiting for your approval...")
        update_report_content(report_id, {"research_plan": plan})
        
        return "pending_approval"


def resume_research_graph(report_id: str):
    config = {"configurable": {"thread_id": report_id}}
    print(f"\n▶️  [RESUMING] Continuing research task for report_id: '{report_id}'")
    
    final_report = None
    
    # We run the loop. If it's empty, output is never created!
    for output in app.stream(None, config):
        for node_name, state_update in output.items():
            print(f"✅ [AGENT UPDATE] '{node_name.upper()}' just finished its task.")
            
            if node_name == "researcher":
                update_report_step(report_id, "Searching the web...")
            elif node_name == "writer":
                update_report_step(report_id, "Drafting the final report...")
            
            if node_name == "writer":
                final_report = state_update["final_report"]
    
    print(f"🏁 [FINISHED] Research complete for report_id: '{report_id}'\n")
    
    # Fallback: Just in case the loop skipped the writer, let's grab it from memory directly
    if final_report is None:
        final_report = app.get_state(config).values.get("final_report")
    
    if hasattr(final_report, "model_dump"):
        final_report_dict = final_report.model_dump()
    else:
        final_report_dict = json.loads(json.dumps(final_report, default=str))
    
    # SAFE CLEANUP: Only delete variables if they actually exist in local memory
    if 'final_report' in locals(): del final_report
    if 'output' in locals(): del output
    if 'node_name' in locals(): del node_name
    if 'state_update' in locals(): del state_update
    
    return final_report_dict
