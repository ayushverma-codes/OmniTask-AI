from langgraph.graph import StateGraph, END
from pipeline.state import AgentState
from components.router import route_request
from components.file_processing import extract_file_content
from components.LLM.intent_analyzer import get_intent_from_llm
from components.Agents.registry import execute_agent

# --- NODE 1: ANALYZER ---
async def analyzer_node(state: AgentState):
    messages = state["messages"]
    last_user_msg = messages[-1]["content"] if messages else ""
    file_path = state.get("current_file_path")
    
    # --- SMART CACHING STRATEGY ---
    # 1. Retrieve existing cache from state
    cached_text = state.get("extracted_content")
    
    # 2. If we have a file, but no cache (new upload), extract NOW.
    if file_path and not cached_text:
        # This blocks briefly while processing, but ensures smooth sailing afterwards
        cached_text = await extract_file_content(file_path)
    
    # Prepare the updates to be returned (this saves cache to DB)
    state_updates = {"extracted_content": cached_text}
    # ------------------------------

    # 3. Router Logic (Now aware of content)
    route = route_request(last_user_msg, file_path)
    action = route.get("action")

    # 4. LLM Fallback
    if action == "analyze_intent":
        # Pass cached text as context so LLM knows what's inside
        preview = cached_text[:2000] if cached_text else "No file context."
        llm_decision = get_intent_from_llm(last_user_msg, preview)
        
        if llm_decision["intent"] == "ambiguous":
            return {
                "next_step": "ask_user", 
                "tool_output": llm_decision["clarification_question"],
                **state_updates
            }
        else:
            return {
                "next_step": "execute", 
                "tool_output": llm_decision["intent"],
                **state_updates
            } 

    if action == "ask_user":
        return {
            "next_step": "ask_user", 
            "tool_output": route["message"],
            **state_updates
        }
    
    if action == "execute":
        return {
            "next_step": "execute", 
            "tool_output": route["agent"],
            **state_updates
        }

    return {"next_step": "error", "tool_output": "System Error", **state_updates}

# --- NODE 2: EXECUTOR ---
async def executor_node(state: AgentState):
    intent = state["tool_output"]
    file_path = state.get("current_file_path")
    # Retrieve the text we just cached
    extracted_text = state.get("extracted_content", "")
    last_message = state["messages"][-1]["content"]

    # Pass the CACHED content to the agent
    result = await execute_agent(intent, last_message, file_path, extracted_text)
    
    return {"messages": [{"role": "assistant", "content": str(result)}]}

# --- NODE 3: RESPONDER ---
async def responder_node(state: AgentState):
    question = state["tool_output"]
    return {"messages": [{"role": "assistant", "content": question}]}

def decide_next_node(state: AgentState):
    return state["next_step"]

# --- GRAPH ---
def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("responder", responder_node)

    workflow.set_entry_point("analyzer")

    # FIXED: Using strings for targets
    workflow.add_conditional_edges(
        "analyzer",
        decide_next_node,
        {
            "execute": "executor",
            "ask_user": "responder",
            "error": "responder" 
        }
    )

    workflow.add_edge("executor", END)
    workflow.add_edge("responder", END)
    return workflow