"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { createClient } from "../utils/supabase/client";

export default function Home() {
  const [ctaLink, setCtaLink] = useState("/login");
  const [isChecking, setIsChecking] = useState(true); // <-- NEW: Loading state

  useEffect(() => {
    const checkAuth = async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        setCtaLink("/dashboard");
      } else {
        setCtaLink("/login");
      }
      setIsChecking(false); // Done checking!
    };
    
    checkAuth();
  }, []);

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center pt-24 px-6 pb-24 text-center">
      
      {/* Hero Section */}
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-900 text-sm font-medium mb-8 shadow-sm">
        <span className="flex h-2 w-2 rounded-full bg-blue-700 animate-pulse"></span>
        Powered by LangGraph & Multi-Agent AI
      </div>
      
      <h1 className="max-w-4xl text-5xl md:text-7xl font-extrabold tracking-tight text-blue-950 mb-6">
        Research faster with an{" "}
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-900 to-emerald-600">
          autonomous AI team.
        </span>
      </h1>
      
      <p className="max-w-2xl text-lg text-slate-600 mb-10 leading-relaxed">
        Stop doing manual due diligence. Our multi-agent system searches the web, analyzes data, and writes fully structured, cited reports in minutes. 
      </p>

      <div className="flex gap-4">
        {/* FIX: Show a pulsing skeleton button while checking Auth to prevent the text flash */}
        {isChecking ? (
          <div className="bg-emerald-600/50 animate-pulse text-transparent px-8 py-3.5 rounded-full font-bold text-lg select-none">
            Loading Button...
          </div>
        ) : (
          <Link 
            href={ctaLink} 
            className="bg-emerald-600 text-white px-8 py-3.5 rounded-full font-bold text-lg hover:bg-emerald-700 shadow-lg shadow-emerald-200 transition-all hover:scale-105 tracking-wide"
          >
            {ctaLink === "/dashboard" ? "Go to Dashboard" : "Start Researching Free"}
          </Link>
        )}
      </div>

      {/* CSS Mockup of AI Dashboard */}
      <div className="mt-20 w-full max-w-5xl rounded-2xl bg-white border border-slate-200 shadow-2xl overflow-hidden flex flex-col text-left">
        <div className="h-12 bg-slate-100 border-b border-slate-200 flex items-center px-4 gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <div className="w-3 h-3 rounded-full bg-amber-400"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
          </div>
          <div className="mx-auto bg-white px-3 py-1 rounded-md text-xs font-mono text-slate-400 border border-slate-200 shadow-sm">
            agentic-research-hub
          </div>
        </div>
        
        <div className="flex flex-1 p-6 md:p-8 gap-8 bg-slate-50">
          <div className="hidden md:flex flex-col gap-4 w-1/4">
            <div className="h-4 bg-slate-200 rounded-md w-3/4"></div>
            <div className="h-4 bg-slate-200 rounded-md w-1/2"></div>
            <div className="h-4 bg-slate-200 rounded-md w-5/6"></div>
            <div className="mt-8 h-4 bg-slate-200 rounded-md w-2/3"></div>
            <div className="h-4 bg-slate-200 rounded-md w-full"></div>
          </div>
          
          <div className="flex-1 bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col gap-4">
            <div className="flex justify-between items-start mb-2">
              <div className="h-6 bg-blue-900 rounded-md w-1/2"></div>
              <div className="h-6 bg-emerald-100 rounded-full w-24"></div>
            </div>
            
            <div className="h-3 bg-slate-100 rounded-full w-full mt-2"></div>
            <div className="h-3 bg-slate-100 rounded-full w-full"></div>
            <div className="h-3 bg-slate-100 rounded-full w-4/5"></div>
            
            <div className="mt-6 bg-blue-950 rounded-lg p-5 flex flex-col gap-3 shadow-inner relative overflow-hidden">
              <div className="flex items-center gap-3 mb-1">
                <div className="w-4 h-4 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin"></div>
                <div className="h-4 bg-white/20 rounded w-1/3"></div>
              </div>
              <div className="flex items-center gap-2 font-mono text-xs text-blue-300">
                <span className="text-emerald-400">❯</span>
                Researcher Agent scraping duckduckgo.com...
              </div>
              <div className="flex items-center gap-2 font-mono text-xs text-blue-300/50">
                <span className="text-emerald-400/50">❯</span>
                Writer Agent drafting executive summary...
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}