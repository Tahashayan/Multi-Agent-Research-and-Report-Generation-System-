import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-6 pb-24 text-center">
      {/* Hero Section */}
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-900 text-sm font-medium mb-8 shadow-sm">
        <span className="flex h-2 w-2 rounded-full bg-blue-700 animate-pulse"></span>
        Powered by LangGraph & Multi-Agent AI
      </div>
      
      <h1 className="max-w-4xl text-5xl md:text-7xl font-extrabold tracking-tight text-blue-950 mb-6">
        Research faster with an{" "}
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-900 to-blue-600">
          autonomous AI team.
        </span>
      </h1>
      
      <p className="max-w-2xl text-lg text-slate-600 mb-10 leading-relaxed">
        Stop doing manual due diligence. Our multi-agent system searches the web, analyzes data, and writes fully structured, cited reports in minutes. 
      </p>

      <div className="flex gap-4">
        <Link 
          href="/login" 
          className="bg-emerald-600 text-white px-8 py-3.5 rounded-full font-semibold text-lg hover:bg-emerald-700 shadow-lg shadow-emerald-200 transition-all hover:scale-105"
        >
          Start Researching Free
        </Link>
        <Link 
          href="https://github.com" 
          target="_blank"
          className="bg-white text-blue-950 border border-slate-200 px-8 py-3.5 rounded-full font-semibold text-lg hover:bg-slate-50 transition-all"
        >
          View Source Code
        </Link>
      </div>

      {/* Feature graphic placeholder */}
      <div className="mt-20 w-full max-w-5xl h-64 md:h-96 rounded-2xl bg-gradient-to-tr from-blue-900 to-slate-800 border border-slate-800 shadow-2xl flex items-center justify-center overflow-hidden">
        <p className="text-blue-200 font-mono text-sm tracking-widest">[ Secure Enterprise Dashboard ]</p>
      </div>
    </div>
  );
}