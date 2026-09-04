import os
import json
import time
import httpx
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)

def fetch_job_from_url(url: str) -> str:
    """
    Fetches job description from URL.
    httpx over requests because FastAPI is async.
    BeautifulSoup strips HTML so LLM only sees clean text.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = httpx.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:4000]
    except Exception as e:
        return f"Could not fetch URL: {str(e)}"

def analyze_job(job_input: str, is_url: bool = False) -> dict:
    """
    Agent 2: Extracts requirements from job description.
    Accepts either a URL or raw job description text.
    Single Responsibility: one agent, one task.
    """
    start_time = time.time()

    if is_url:
        job_text = fetch_job_from_url(job_input)
    else:
        job_text = job_input

    system_prompt = """You are an expert job description analyzer.
    Always respond with valid JSON only, no markdown, no explanation.

    Extract:
    {
        "job_title": "title",
        "company": "company name if mentioned",
        "required_skills": ["skill1"],
        "nice_to_have_skills": ["skill1"],
        "required_experience_years": number or null,
        "required_education": "degree requirement",
        "key_responsibilities": ["resp1"],
        "tech_stack": ["tech1"],
        "soft_skills_required": ["skill1"],
        "seniority_level": "junior/mid/senior/staff"
    }"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Analyze this job description:\n\n{job_text}")
    ]

    response = llm.invoke(messages)
    latency = int((time.time() - start_time) * 1000)

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        parsed = {"raw_text": job_text[:500], "parse_error": True}

    return {
        "data": parsed,
        "latency_ms": latency,
        "agent": "job_analyzer"
    }