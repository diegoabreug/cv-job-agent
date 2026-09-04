import os
import json
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# temperature=0.3 here (not 0) because recommendations
# benefit from slight creativity — we want varied, specific
# suggestions. Not too high or outputs become unreliable.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

def generate_recommendations(cv_data: dict, job_data: dict,
                              gap_data: dict) -> dict:
    """
    Agent 4: Generates actionable recommendations.
    Receives all previous agent outputs — this is the synthesis layer.
    Highest-value output for the user.
    """
    start_time = time.time()

    system_prompt = """You are a senior career coach.
    Generate specific, actionable recommendations in English.
    Always respond with valid JSON only, no markdown, no explanation.

    Format:
    {
        "immediate_actions": [
            {
                "category": "CV Improvement|Skill Gap|Application Strategy",
                "recommendation": "specific action",
                "priority": "high|medium|low",
                "time_estimate": "1 day|1 week|1 month"
            }
        ],
        "cv_improvements": ["specific improvement"],
        "skills_to_acquire": [
            {
                "skill": "skill name",
                "reason": "why it matters for this role",
                "free_resource": "course or resource"
            }
        ],
        "application_advice": "specific advice for this application",
        "interview_prep_focus": ["topic1", "topic2"]
    }"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
        CANDIDATE: {json.dumps(cv_data, indent=2)}
        JOB: {json.dumps(job_data, indent=2)}
        GAPS IDENTIFIED: {json.dumps(gap_data, indent=2)}

        Generate specific recommendations to improve this candidate's
        chances for this specific role.
        """)
    ]

    response = llm.invoke(messages)
    latency = int((time.time() - start_time) * 1000)

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        parsed = {"error": "Could not generate recommendations"}

    return {
        "data": parsed,
        "latency_ms": latency,
        "agent": "recommender"
    }