"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "../../utils/supabase/client";

export default function HistoryPage() {
  const router = useRouter();
  const supabase = createClient();

  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedReportId, setExpandedReportId] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      // 1. Check Auth
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }

      // 2. Fetch reports from FastAPI backend
      try {
        const response = await fetch(`http://localhost:8000/user-reports/${user.id}`);
        const data = await response.json();
        setReports(data);
      } catch (error) {
        console.error("Failed to fetch history", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [router, supabase]);

  const toggleReport = (id: string) => {
    if (expandedReportId === id) {
      setExpandedReportId(null);
    } else {
      setExpandedReportId(id);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 p-6 md:p-12">
      <div className="max-w-5xl mx-auto mb-10">
        <h1 className="text-3xl font-extrabold text-blue-950 tracking-tight">Research History</h1>
        <p className="text-slate-500 mt-2">Access all your previously generated AI reports.</p>
      </div>

      <div className="max-w-5xl mx-auto">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : reports.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
            <h3 className="text-xl font-bold text-slate-700 mb-2">No reports found</h3>
            <p className="text-slate-500 mb-6">You haven't generated any AI research reports yet.</p>
            <button 
              onClick={() => router.push("/dashboard")}
              className="bg-blue-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-800 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {reports.map((report) => {
              const isCompleted = report.status === "completed";
              const isExpanded = expandedReportId === report.id;
              
              return (
                <div 
                  key={report.id} 
                  className={`bg-white border rounded-2xl overflow-hidden transition-all duration-300 ${
                    isExpanded ? "md:col-span-2 shadow-xl border-blue-200" : "shadow-sm border-slate-200 hover:shadow-md hover:border-blue-100"
                  }`}
                >
                  {/* Card Header */}
                  <div className="p-6 flex justify-between items-start gap-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                          isCompleted ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                        }`}>
                          {report.status.replace("_", " ")}
                        </span>
                        <span className="text-sm text-slate-400 font-medium">
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <h2 className="text-xl font-bold text-blue-950 capitalize">{report.topic}</h2>
                    </div>

                    {isCompleted && (
                      <button 
                        onClick={() => toggleReport(report.id)}
                        className={`shrink-0 px-4 py-2 rounded-lg text-sm font-bold transition-colors ${
                          isExpanded ? "bg-slate-100 text-slate-600 hover:bg-slate-200" : "bg-blue-50 text-blue-700 border border-blue-100 hover:bg-blue-100"
                        }`}
                      >
                        {isExpanded ? "Close" : "View Report"}
                      </button>
                    )}
                  </div>

                  {/* Expanded Report Content */}
                  {isExpanded && report.content && (
                    <div className="border-t border-slate-100 bg-slate-50 p-6 md:p-10">
                      <div className="mb-8">
                        <h3 className="text-sm uppercase tracking-wider font-bold text-blue-800 mb-3">Executive Summary</h3>
                        <p className="text-slate-700 text-lg leading-relaxed">{report.content.executive_summary}</p>
                      </div>

                      <div className="mb-8">
                        <h3 className="text-sm uppercase tracking-wider font-bold text-blue-800 mb-4">Key Data Points</h3>
                        <ul className="grid gap-3">
                          {report.content.key_data_points?.map((point: string, index: number) => (
                            <li key={index} className="flex gap-4 items-start bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold mt-0.5">
                                {index + 1}
                              </span>
                              <span className="text-slate-700 leading-relaxed">{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="bg-blue-950 text-slate-50 p-6 md:p-8 rounded-2xl shadow-inner">
                        <h3 className="text-sm uppercase tracking-wider font-bold text-emerald-400 mb-3">Conclusion</h3>
                        <p className="text-slate-200 leading-relaxed">{report.content.conclusion}</p>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}