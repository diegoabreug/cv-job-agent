import os
from supabase import create_client, Client
from dotenv import load_dotenv
import time

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def create_analysis(cv_text: str, job_description: str, job_url: str = None) -> str:
    result = supabase.table("analyses").insert({
        "cv_text": cv_text[:500],
        "job_description": job_description[:500],
        "job_url": job_url,
        "status": "processing"
    }).execute()
    return result.data[0]["id"]

def log_agent_step(analysis_id: str, agent_name: str,
                   input_summary: str, output_summary: str,
                   latency_ms: int):
    """
    Logs each agent step for observability.
    Every decision, every input/output, every latency is recorded.
    This is how we answer 'how do you observe the agent'.
    """
    supabase.table("agent_logs").insert({
        "analysis_id": analysis_id,
        "agent_name": agent_name,
        "input_summary": input_summary[:300],
        "output_summary": output_summary[:300],
        "latency_ms": latency_ms
    }).execute()

def save_recommendations(analysis_id: str, recommendations: list):
    for rec in recommendations:
        supabase.table("recommendations").insert({
            "analysis_id": analysis_id,
            "category": rec.get("category"),
            "recommendation": rec.get("recommendation"),
            "priority": rec.get("priority")
        }).execute()

def update_analysis_score(analysis_id: str, score: int):
    supabase.table("analyses").update({
        "match_score": score,
        "status": "completed"
    }).eq("id", analysis_id).execute()