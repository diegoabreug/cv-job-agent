import os
import json
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# Why Groq: free tier, fast inference, Llama 3.1 70B is strong
# for structured extraction tasks
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,  # 0 = deterministic, important for structured extraction
)

def parse_cv(cv_text: str) -> dict:
    """
    Agent 1: Extracts structured information from CV text in English.
    Temperature=0 because we want consistent, reliable extraction every time.
    """
    start_time = time.time()

    system_prompt = """You are an expert CV analyzer. Extract information from CVs written in English.
    Always respond with valid JSON only, no markdown, no explanation.

    Extract the following structure:
    {
        "name": "candidate full name",
        "skills": ["skill1", "skill2"],
        "experience_years": number,
        "education": "highest degree and field",
        "languages": ["language1"],
        "recent_roles": ["role1", "role2"],
        "key_achievements": ["achievement1"],
        "technologies": ["tech1", "tech2"],
        "soft_skills": ["skill1"]
    }"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Parse this CV:\n\n{cv_text}")
    ]

    response = llm.invoke(messages)
    latency = int((time.time() - start_time) * 1000)

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        parsed = {"raw_text": cv_text[:500], "parse_error": True}

    return {
        "data": parsed,
        "latency_ms": latency,
        "agent": "cv_parser"
    }