"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { GlassCard } from "@/components/GlassCard";
import { tailorResume, checkHealth, getMasterResume } from "@/lib/api";
import { showToast } from "@/components/Toast";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import Link from "next/link";

export default function Home() {
  const [jd, setJd] = useState("");
  const [customInstructions, setCustomInstructions] = useState("");
  const [loading, setLoading] = useState(false);
  const [agyInstalled, setAgyInstalled] = useState(true);
  const [hasMasterResume, setHasMasterResume] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkHealth().then(data => {
      setAgyInstalled(data.agy_installed);
    }).catch(() => {
      // Ignore network errors for health check, assume bad until otherwise
    });

    getMasterResume().then(content => {
      setHasMasterResume(content.trim().length > 0);
    }).catch(() => {});
  }, []);

  const handleTailor = async () => {
    if (!jd.trim()) {
      showToast("Error", "Please paste a job description.");
      return;
    }
    
    setLoading(true);
    try {
      const result = await tailorResume(jd, customInstructions);
      sessionStorage.setItem("tailor_result", JSON.stringify(result));
      router.push("/result");
    } catch (err: any) {
      setLoading(false);
      showToast(err.error || "Error", err.hint || "Something went wrong.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-10 flex flex-col gap-8 pb-12">
      <LoadingOverlay isVisible={loading} />
      
      {!agyInstalled && (
        <div className="surface-panel p-4 border border-red-500/30 bg-red-500/10 text-red-200 rounded-2xl flex items-start gap-3">
          <svg className="w-5 h-5 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          <div>
            <h3 className="font-semibold mb-1">AI Engine Not Found</h3>
            <p className="text-sm opacity-80">The `agy` CLI is either missing from your PATH or not authenticated. Please install and authenticate the Antigravity CLI to use the resume tailoring engine.</p>
          </div>
        </div>
      )}

      {!hasMasterResume && (
        <div className="surface-panel p-4 border border-amber-500/30 bg-amber-500/10 text-amber-200 rounded-2xl flex items-start gap-3">
          <svg className="w-5 h-5 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <div>
            <h3 className="font-semibold mb-1">Master Resume Missing</h3>
            <p className="text-sm opacity-80 mb-2">You need to import your master resume before you can tailor it to a job description.</p>
            <Link href="/editor" className="text-sm font-semibold hover:underline" style={{ color: 'var(--accent-orange)' }}>
              Go to Master Resume &rarr;
            </Link>
          </div>
        </div>
      )}

      <div className="text-center mb-4">
        <h1 className="display-title mb-4">
          Land your dream job.
        </h1>
        <p className="body-text" style={{ color: 'var(--label-secondary)' }}>
          Paste the job description below. We'll cross-reference it with your Master Resume and generate a perfectly tailored version without inventing any false information.
        </p>
      </div>

      <GlassCard className="flex flex-col gap-4">
        <textarea
          className="w-full h-64 p-4 text-sm"
          placeholder="Paste the full Job Description here..."
          value={jd}
          onChange={e => setJd(e.target.value)}
        />
        <textarea
          className="w-full h-24 p-4 text-sm"
          placeholder="Optional: Custom instructions (e.g., 'Focus heavily on React, ignore backend skills, keep it under 1 page')"
          value={customInstructions}
          onChange={e => setCustomInstructions(e.target.value)}
        />
        <div className="flex justify-end">
          <button 
            onClick={handleTailor} 
            className="btn-primary" 
            disabled={loading || !agyInstalled || !hasMasterResume}
            style={{ opacity: (!agyInstalled || !hasMasterResume) ? 0.5 : 1 }}
          >
            Tailor My Resume
          </button>
        </div>
      </GlassCard>
    </div>
  );
}
