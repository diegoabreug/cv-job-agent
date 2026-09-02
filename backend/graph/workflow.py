from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.cv_parser import parse_cv
from agents.job_analyzer import analyze_job
from agents.gap_analyzer import analyze_gaps
from agents.recommender import generate_recommendations
from db.supabase_client import (
    create_analysis, log_agent_step,
    save_recommendations, update_analysis_score
)

class AgentState(TypedDict):
    cv_text: str
    job_input: str
    is_url: bool
    analysis_id: str
    cv_data: Optional[dict]
    job_data: Optional[dict]
    gap_data: Optional[dict]
    recommendations: Optional[dict]
    error: Optional[str]

def node_parse_cv(state: AgentState) -> AgentState:
    """Node 1: Parse the CV."""
    try:
        result = parse_cv(state["cv_text"])
        log_agent_step(
            state["analysis_id"],
            "cv_parser",
            f"CV text length: {len(state['cv_text'])} chars",
            f"Extracted {len(result['data'].get('skills', []))} skills",
            result["latency_ms"]
        )
        return {**state, "cv_data": result["data"]}
    except Exception as e:
        return {**state, "error": str(e)}

def node_analyze_job(state: AgentState) -> AgentState:
    """Node 2: Analyze the job description."""
    try:
        result = analyze_job(state["job_input"], state["is_url"])
        log_agent_step(
            state["analysis_id"],
            "job_analyzer",
            f"Job input type: {'URL' if state['is_url'] else 'text'}",
            f"Found {len(result['data'].get('required_skills', []))} required skills",
            result["latency_ms"]
        )
        return {**state, "job_data": result["data"]}
    except Exception as e:
        return {**state, "error": str(e)}

def node_analyze_gaps(state: AgentState) -> AgentState:
    """Node 3: Compare CV vs job requirements."""
    try:
        result = analyze_gaps(state["cv_data"], state["job_data"])
        log_agent_step(
            state["analysis_id"],
            "gap_analyzer",
            f"Comparing {len(state['cv_data'].get('skills', []))} candidate skills",
            f"Match score: {result['data'].get('match_score', 0)}%",
            result["latency_ms"]
        )
        return {**state, "gap_data": result["data"]}
    except Exception as e:
        return {**state, "error": str(e)}

def node_generate_recommendations(state: AgentState) -> AgentState:
    """Node 4: Generate actionable recommendations."""
    try:
        result = generate_recommendations(
            state["cv_data"],
            state["job_data"],
            state["gap_data"]
        )

        recs = result["data"].get("immediate_actions", [])
        save_recommendations(state["analysis_id"], recs)
        update_analysis_score(
            state["analysis_id"],
            state["gap_data"].get("match_score", 0)
        )

        log_agent_step(
            state["analysis_id"],
            "recommender",
            f"Gap score: {state['gap_data'].get('match_score')}%",
            f"Generated {len(recs)} recommendations",
            result["latency_ms"]
        )
        return {**state, "recommendations": result["data"]}
    except Exception as e:
        return {**state, "error": str(e)}

def should_continue(state: AgentState) -> str:
    """
    Conditional edge — key LangGraph feature.
    If any agent fails we stop the graph immediately.
    This is routing logic based on state — not possible
    with simple sequential function calls.
    """
    if state.get("error"):
        return "end"
    return "continue"

def build_workflow() -> StateGraph:
    """
    Builds the LangGraph workflow.
    State is explicit and inspectable at every step.
    Easy to add parallel execution later.
    Industry standard for production agentic systems.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_cv", node_parse_cv)
    workflow.add_node("analyze_job", node_analyze_job)
    workflow.add_node("analyze_gaps", node_analyze_gaps)
    workflow.add_node("generate_recommendations", node_generate_recommendations)

    workflow.set_entry_point("parse_cv")

    workflow.add_conditional_edges(
        "parse_cv",
        should_continue,
        {"continue": "analyze_job", "end": END}
    )
    workflow.add_conditional_edges(
        "analyze_job",
        should_continue,
        {"continue": "analyze_gaps", "end": END}
    )
    workflow.add_conditional_edges(
        "analyze_gaps",
        should_continue,
        {"continue": "generate_recommendations", "end": END}
    )
    workflow.add_edge("generate_recommendations", END)

    return workflow.compile()

# Compile once, reuse across all requests
agent_workflow = build_workflow()