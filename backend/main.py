from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.pdf_reader import extract_text_from_pdf
from db.supabase_client import create_analysis, supabase
from graph.workflow import agent_workflow
import uvicorn

app = FastAPI(
    title="CV Job Match Agent",
    description="Agentic system for CV-Job matching using LangGraph + Groq",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "agents": 4}

@app.post("/analyze")
async def analyze_cv(
    cv_file: UploadFile = File(...),
    job_input: str = Form(...),
    is_url: bool = Form(False)
):
    """
    Main endpoint — accepts CV PDF + job description or URL.
    Runs the full 4-agent LangGraph workflow.
    """
    if not cv_file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")

    cv_bytes = await cv_file.read()
    cv_text = extract_text_from_pdf(cv_bytes)

    if not cv_text or len(cv_text) < 100:
        raise HTTPException(400, "Could not extract text from PDF")

    analysis_id = create_analysis(cv_text, job_input)

    initial_state = {
        "cv_text": cv_text,
        "job_input": job_input,
        "is_url": is_url,
        "analysis_id": analysis_id,
        "cv_data": None,
        "job_data": None,
        "gap_data": None,
        "recommendations": None,
        "error": None
    }

    result = agent_workflow.invoke(initial_state)

    if result.get("error"):
        raise HTTPException(500, f"Agent error: {result['error']}")

    return {
        "analysis_id": analysis_id,
        "match_score": result["gap_data"].get("match_score", 0),
        "cv_profile": result["cv_data"],
        "job_requirements": result["job_data"],
        "gaps": result["gap_data"],
        "recommendations": result["recommendations"]
    }

@app.get("/analysis/{analysis_id}/logs")
async def get_agent_logs(analysis_id: str):
    """
    Observability endpoint — shows every agent step,
    decision, and latency. This is how we monitor the agent.
    """
    logs = supabase.table("agent_logs")\
        .select("*")\
        .eq("analysis_id", analysis_id)\
        .order("created_at")\
        .execute()
    return {"logs": logs.data}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)