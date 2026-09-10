"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "../../utils/supabase/client";

interface FinalReport {
  title: string;
  executive_summary: string;
  key_data_points: string[];
  conclusion: string;
}

export default function Dashboard() {
  const router = useRouter();
  const supabase = createClient();

  const [topic, setTopic] = useState("");
  const [reportId, setReportId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [currentStep, setCurrentStep] = useState<string>("");
  const [finalReport, setFinalReport] = useState<FinalReport | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login"); 
      } else {
        setUserEmail(user.email || null);
      }
    };
    checkUser();
  }, [router, supabase]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  const handleGenerate = async () => {
    if (!topic) return;
    setStatus("pending");
    setCurrentStep("Initializing AI agents...");
    setFinalReport(null);

    try {
      const response = await fetch("http://localhost:8000/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      const data = await response.json();
      setReportId(data.id);
    } catch (error) {
      setStatus("failed");
    }
  };

  const handleApprove = async () => {
    if (!reportId) return;
    setStatus("researching");
    await fetch(`http://localhost:8000/approve-report/${reportId}`, { method: "POST" });
  };

  const fetchFinalReport = async (id: string) => {
    const response = await fetch(`http://localhost:8000/report/${id}`);
    const data = await response.json();
    setFinalReport(data.content);
  };

  useEffect(() => {
    if (!reportId) return;
    const eventSource = new EventSource(`http://localhost:8000/stream-status/${reportId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setCurrentStep(data.step);
      setStatus(data.status);

      if (data.status === "completed") {
        eventSource.close();
        fetchFinalReport(reportId);
      }
      if (data.status === "failed") eventSource.close();
    };

    return () => eventSource.close();
  }, [reportId]);

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 p-6 md:p-12">
      <div className="max-w-4xl mx-auto mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-blue-950 tracking-tight">Research Hub</h1>
          <p className="text-slate-500 mt-1">Logged in as <span className="font-medium">{userEmail}</span></p>
        </div>
        <button onClick={handleSignOut} className="text-sm font-medium text-slate-500 hover:text-red-600 transition-colors">
          Sign Out
        </button>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Input Card */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
          <label className="block text-sm font-bold text-blue-950 mb-3 uppercase tracking-wide">Research Topic</label>
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              className="flex-1 border border-slate-300 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 transition-all text-slate-900 placeholder:text-slate-400 shadow-inner"
              placeholder="e.g., SpaceX Starship vs NASA SLS payload cost..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={status === "pending" || status === "researching"}
            />
            <button
              onClick={handleGenerate}
              disabled={status === "pending" || status === "researching"}
              className="bg-emerald-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-emerald-200 tracking-wide"
            >
              Generate Report
            </button>
          </div>
        </div>

        {/* Live Progress Card */}
        {(status !== "idle" && status !== "completed") && (
          <div className="bg-blue-900 p-8 rounded-2xl border border-blue-800 shadow-xl relative overflow-hidden">
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-4">
                {(status === "pending" || status === "researching") && (
                  <div className="w-6 h-6 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
                )}
                <h3 className="text-xl font-bold text-white">
                  {status === "pending_approval" ? "Human Approval Required" : "AI Team is Working"}
                </h3>
              </div>
              
              <div className="bg-blue-950/50 border border-blue-800 p-4 rounded-xl font-mono text-sm text-blue-200 shadow-inner">
                <span className="text-emerald-400 mr-2">❯</span>
                {currentStep}
              </div>

              {status === "pending_approval" && (
                <div className="mt-6 pt-6 border-t border-blue-800">
                  <p className="text-sm text-blue-100 mb-4 font-medium">
                    The Planning Agent has outlined the research strategy. Please approve to deploy the web scrapers.
                  </p>
                  <button
                    onClick={handleApprove}
                    className="bg-emerald-500 text-white px-8 py-2.5 rounded-lg font-bold hover:bg-emerald-600 transition-colors shadow-lg shadow-emerald-900"
                  >
                    Approve & Execute
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Final Report Card */}
        {finalReport && (
          <div className="bg-white p-8 md:p-12 rounded-2xl shadow-xl shadow-blue-900/5 border border-slate-200">
            <div className="mb-10 pb-8 border-b border-slate-100">
              <h1 className="text-3xl md:text-4xl font-extrabold text-blue-950 mb-6 leading-tight">{finalReport.title}</h1>
              <h3 className="text-sm uppercase tracking-wider font-bold text-blue-800 mb-3">Executive Summary</h3>
              <p className="text-slate-700 text-lg leading-relaxed">{finalReport.executive_summary}</p>
            </div>

            <div className="mb-10">
              <h3 className="text-sm uppercase tracking-wider font-bold text-blue-800 mb-4">Key Data Points</h3>
              <ul className="grid gap-4">
                {finalReport.key_data_points.map((point, index) => (
                  <li key={index} className="flex gap-4 items-start bg-slate-50 p-4 rounded-xl border border-slate-100">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-900 flex items-center justify-center text-sm font-bold mt-0.5">
                      {index + 1}
                    </span>
                    <span className="text-slate-700 leading-relaxed">{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Navy Blue Conclusion Box */}
            <div className="bg-blue-950 text-slate-50 p-8 rounded-2xl shadow-inner">
              <h3 className="text-sm uppercase tracking-wider font-bold text-emerald-400 mb-3">Conclusion</h3>
              <p className="text-slate-200 text-lg leading-relaxed">{finalReport.conclusion}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}