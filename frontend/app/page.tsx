"use client";

import { useState } from "react";

interface AnalysisResult {
  analysis_id: string;
  match_score: number;
  cv_profile: {
    name: string;
    skills: string[];
    experience_years: number;
    education: string;
  };
  gaps: {
    match_score: number;
    matching_skills: string[];
    missing_required_skills: string[];
    critical_gaps: string[];
    overall_assessment: string;
    strengths: string[];
  };
  recommendations: {
    immediate_actions: {
      category: string;
      recommendation: string;
      priority: string;
      time_estimate: string;
    }[];
    skills_to_acquire: {
      skill: string;
      reason: string;
      free_resource: string;
    }[];
    application_advice: string;
    interview_prep_focus: string[];
  };
}

export default function Home() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [jobInput, setJobInput] = useState("");
  const [isUrl, setIsUrl] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!cvFile || !jobInput) {
      setError("Please upload a CV and enter a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("cv_file", cvFile);
    formData.append("job_input", jobInput);
    formData.append("is_url", String(isUrl));

    try {
      const response = await fetch("https://cv-job-agent.onrender.com/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Analysis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-green-600";
    if (score >= 45) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 70) return "bg-green-100 border-green-300";
    if (score >= 45) return "bg-yellow-100 border-yellow-300";
    return "bg-red-100 border-red-300";
  };

  const getPriorityColor = (priority: string) => {
    if (priority === "high") return "bg-red-100 text-red-700";
    if (priority === "medium") return "bg-yellow-100 text-yellow-700";
    return "bg-gray-100 text-gray-700";
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            CV Job Match Agent
          </h1>
          <p className="text-gray-500 mt-1 text-sm">
            4-agent AI system powered by LangGraph + Groq — analyzes your CV
            against any job description
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Input Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
          <h2 className="font-semibold text-gray-800">Upload & Analyze</h2>

          {/* CV Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CV / Resume (PDF only)
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setCvFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-gray-900 file:text-white hover:file:bg-gray-700 cursor-pointer"
            />
            {cvFile && (
              <p className="text-xs text-green-600 mt-1">
                ✓ {cvFile.name} selected
              </p>
            )}
          </div>

          {/* Job Input Toggle */}
          <div>
            <div className="flex items-center gap-4 mb-3">
              <label className="block text-sm font-medium text-gray-700">
                Job Description
              </label>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsUrl(false)}
                  className={`text-xs px-3 py-1 rounded-full transition-colors ${
                    !isUrl
                      ? "bg-gray-900 text-white"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  Paste text
                </button>
                <button
                  onClick={() => setIsUrl(true)}
                  className={`text-xs px-3 py-1 rounded-full transition-colors ${
                    isUrl
                      ? "bg-gray-900 text-white"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  URL
                </button>
              </div>
            </div>
            <textarea
              value={jobInput}
              onChange={(e) => setJobInput(e.target.value)}
              placeholder={
                isUrl
                  ? "https://company.com/jobs/software-engineer"
                  : "Paste the full job description here..."
              }
              rows={5}
              className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 resize-none"
            />
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 px-4 py-2 rounded-lg">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-gray-900 text-white py-3 rounded-lg font-medium text-sm hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  />
                </svg>
                Running 4 agents...
              </span>
            ) : (
              "Analyze Match"
            )}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Score Card */}
            <div
              className={`rounded-xl border-2 p-6 ${getScoreBg(result.match_score)}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Match Score
                  </p>
                  <p
                    className={`text-5xl font-bold mt-1 ${getScoreColor(result.match_score)}`}
                  >
                    {result.match_score}
                    <span className="text-2xl">%</span>
                  </p>
                  <p className="text-sm text-gray-600 mt-2 max-w-lg">
                    {result.gaps.overall_assessment}
                  </p>
                </div>
                <div className="text-right text-sm text-gray-500">
                  <p className="font-medium text-gray-700">
                    {result.cv_profile.name}
                  </p>
                  <p>{result.cv_profile.education}</p>
                  <p>{result.cv_profile.experience_years} years experience</p>
                  <p className="text-xs mt-2 font-mono text-gray-400">
                    ID: {result.analysis_id.slice(0, 8)}...
                  </p>
                </div>
              </div>
            </div>

            {/* Two Column */}
            <div className="grid grid-cols-2 gap-4">
              {/* Strengths */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-800 mb-3 text-sm">
                  ✅ Strengths
                </h3>
                <ul className="space-y-1">
                  {result.gaps.strengths.map((s, i) => (
                    <li key={i} className="text-xs text-gray-600 flex gap-2">
                      <span className="text-green-500 mt-0.5">•</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Critical Gaps */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-800 mb-3 text-sm">
                  ⚠️ Critical Gaps
                </h3>
                <ul className="space-y-1">
                  {result.gaps.critical_gaps.map((g, i) => (
                    <li key={i} className="text-xs text-gray-600 flex gap-2">
                      <span className="text-red-500 mt-0.5">•</span>
                      {g}
                    </li>
                  ))}
                </ul>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-500 font-medium mb-1">
                    Missing required skills
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {result.gaps.missing_required_skills.map((s, i) => (
                      <span
                        key={i}
                        className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Immediate Actions */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-800 mb-4 text-sm">
                🎯 Immediate Actions
              </h3>
              <div className="space-y-3">
                {result.recommendations.immediate_actions.map((action, i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-medium ${getPriorityColor(action.priority)}`}
                        >
                          {action.priority}
                        </span>
                        <span className="text-xs text-gray-400">
                          {action.category}
                        </span>
                        <span className="text-xs text-gray-400 ml-auto">
                          {action.time_estimate}
                        </span>
                      </div>
                      <p className="text-xs text-gray-700">
                        {action.recommendation}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skills to Acquire */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-800 mb-4 text-sm">
                📚 Skills to Acquire
              </h3>
              <div className="space-y-3">
                {result.recommendations.skills_to_acquire.map((skill, i) => (
                  <div key={i} className="border border-gray-100 rounded-lg p-3">
                    <p className="text-sm font-medium text-gray-800">
                      {skill.skill}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">{skill.reason}</p>
                    <p className="text-xs text-blue-600 mt-1">
                      📖 {skill.free_resource}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Interview Prep */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-800 mb-3 text-sm">
                🎤 Interview Prep Focus
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.recommendations.interview_prep_focus.map((topic, i) => (
                  <span
                    key={i}
                    className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full"
                  >
                    {topic}
                  </span>
                ))}
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-700">
                  <span className="font-medium">Application advice: </span>
                  {result.recommendations.application_advice}
                </p>
              </div>
            </div>

            {/* Agent Logs Link */}
            <div className="bg-gray-900 rounded-xl p-4">
              <p className="text-xs text-gray-400 font-mono">
                Observability → Agent logs stored in Supabase
              </p>
              <p className="text-xs text-gray-500 font-mono mt-1">
                GET /analysis/{result.analysis_id}/logs
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}