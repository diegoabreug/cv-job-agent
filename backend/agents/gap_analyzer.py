import os
import json
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def analyze_gaps(cv_data: dict, job_data: dict) -> dict:
    """
    Agent 3: Compares CV against job requirements.
    Separate agent because gap analysis requires reasoning
    across two data sources independently from parsing.
    match_score (0-100) is our primary output KPI.
    """
    start_time = time.time()

    system_prompt = """You are an expert career advisor analyzing candidate-job fit.
    Always respond with valid JSON only, no markdown, no explanation.

    Provide:
    {
        "match_score": 0-100,
        "matching_skills": ["skill1"],
        "missing_required_skills": ["skill1"],
        "missing_nice_to_have": ["skill1"],
        "experience_gap": "description or null",
        "education_fit": "meets/below/exceeds requirements",
        "strengths": ["strength1"],
        "critical_gaps": ["gap1"],
        "overall_assessment": "brief honest assessment"
    }"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
        CANDIDATE PROFILE:
        {json.dumps(cv_data, indent=2)}

        JOB REQUIREMENTS:
        {json.dumps(job_data, indent=2)}

        Analyze the fit between this candidate and this job.
        Be honest and specific.
        """)
    ]

    response = llm.invoke(messages)
    latency = int((time.time() - start_time) * 1000)

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        parsed = {"match_score": 0, "parse_error": True}

    return {
        "data": parsed,
        "latency_ms": latency,
        "agent": "gap_analyzer"
    }