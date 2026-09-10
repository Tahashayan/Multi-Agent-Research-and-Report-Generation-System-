import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agentic - AI Research SaaS",
  description: "Multi-Agent AI for deep market research.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 text-slate-900 antialiased`}>
        {/* Global Navigation Bar */}
        <nav className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/80 backdrop-blur-md">
          <div className="mx-auto max-w-7xl px-6 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-900 to-blue-700 flex items-center justify-center shadow-sm">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="font-bold text-xl tracking-tight text-blue-950">Agentic.ai</span>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-emerald-600 transition-colors">
                Sign In
              </Link>
              <Link href="/dashboard" className="text-sm font-medium bg-emerald-600 text-white px-5 py-2 rounded-full hover:bg-emerald-700 transition-all shadow-sm">
                Dashboard
              </Link>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}