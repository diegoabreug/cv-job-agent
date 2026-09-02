# CV Job Match Agent

An agentic AI system that analyzes a candidate's CV against any job description using a 4-agent LangGraph pipeline powered by Groq LLMs.

🔗 **Live Demo:** https://frontend-five-tau-a92oojj0mf.vercel.app  
📡 **API Docs:** https://cv-job-agent.onrender.com/docs

---

## Architecture

CV (PDF) + Job Description
↓
FastAPI Backend
↓
LangGraph Orchestrator
↓
┌─────────────────────────────────┐
│ Agent 1 → CV Parser │
│ Agent 2 → Job Analyzer │
│ Agent 3 → Gap Analyzer │
│ Agent 4 → Recommender │
└─────────────────────────────────┘
↓
Supabase (observability logs)
↓
Next.js Frontend (Vercel)


## Tech Stack

**Backend**
- Python + FastAPI
- LangGraph (agent orchestration)
- Groq API (LLM inference — free tier)
- PyPDF2 (CV text extraction)
- Supabase (PostgreSQL — agent logs & results)

**Frontend**
- Next.js 14 + TypeScript
- Tailwind CSS
- Deployed on Vercel

**Infrastructure**
- Backend: Render (free tier)
- Database: Supabase (free tier)
- Frontend: Vercel (free tier)
- Total infrastructure cost: $0

## How It Works

1. User uploads their CV as PDF and pastes a job description
2. **Agent 1 (CV Parser)** extracts structured profile data from the CV
3. **Agent 2 (Job Analyzer)** extracts requirements from the job description
4. **Agent 3 (Gap Analyzer)** compares both and produces a match score (0-100)
5. **Agent 4 (Recommender)** generates actionable recommendations with free resources
6. Every agent step is logged to Supabase with input, output, and latency

## Observability

Every analysis is traceable via:

GET /analysis/{analysis_id}/logs


Each log entry contains:
- Agent name
- Input summary
- Output summary  
- Latency in milliseconds
- Timestamp

## Running Locally

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env with:
# GROQ_API_KEY=your_key
# SUPABASE_URL=your_url
# SUPABASE_KEY=your_key

python main.py
# API running at http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev
# UI running at http://localhost:3000
```

## Agent Design Decisions

- **LangGraph over simple LangChain**: State is explicit and inspectable at every step. Conditional routing stops the pipeline if any agent fails.
- **Groq over OpenAI**: Free tier with fast inference. No credit card required to get started.
- **Temperature=0 for parsers**: Deterministic extraction for CV and job parsing. Temperature=0.3 for the recommender to allow creative, varied suggestions.
- **Supabase for observability**: Every agent decision is logged — not just the final result. This allows debugging and quality assessment at each step.

## Author

Diego Enrique Abreu Garcia  
Software Engineer | U.S. Permanent Resident  
[LinkedIn](https://linkedin.com/in/diegoabreug) · [GitHub](https://github.com/diegoabreug)