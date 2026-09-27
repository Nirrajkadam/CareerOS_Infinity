'use client';

import { apiFetch } from '../../../lib/apiClient';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Building2, 
  MapPin, 
  Target, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  ArrowLeft, 
  Send, 
  ShieldCheck
} from 'lucide-react';

export default function JobDetailPage({ params }: { params: { id: string } }) {
  const searchParams = useSearchParams();
  const router = useRouter();

  const title = searchParams.get('title') || 'Data Engineer';
  const company = searchParams.get('company') || 'Target Employer';
  const portalUrl = searchParams.get('url') || 'https://www.naukri.com/data-engineer-jobs';

  const [prepareError, setPrepareError] = useState('');
  const [preparing, setPreparing] = useState(false);
  const [tailoring, setTailoring] = useState(false);
  const [tailoredResume, setTailoredResume] = useState<string | null>(null);

  // Dynamic Keyword Breakdown computation based on role title
  const titleLower = title.toLowerCase();
  const isIntern = titleLower.includes('intern') || titleLower.includes('internship');
  const isSecurity = titleLower.includes('security');
  const isAI = titleLower.includes('ai') || titleLower.includes('machine learning');
  const isBackend = titleLower.includes('backend') || titleLower.includes('system');

  const matchedKeywords = isSecurity 
    ? ['Python', 'Linux', 'Git', 'REST API'] 
    : isAI 
    ? ['Python', 'PostgreSQL', 'FastAPI', 'Pytest'] 
    : isBackend 
    ? ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'System Design']
    : ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'ETL Pipelines'];

  const missingKeywords = isSecurity 
    ? ['Security Audit', 'Penetration Testing', 'Vulnerability Scan'] 
    : isAI 
    ? ['PyTorch', 'TensorFlow', 'LLM Embeddings'] 
    : isBackend 
    ? ['Microservices', 'Kubernetes', 'gRPC']
    : ['Apache Spark', 'Kafka', 'Snowflake'];

  const matchScore = isIntern ? 92 : isSecurity ? 68 : isAI ? 74 : isBackend ? 85 : 88;

  async function handlePrepareApplication() {
    setPreparing(true);
    setPrepareError('');
    try {
      const data = await apiFetch<{ application_id: string }>('/api/v1/applications/apply', {
        method: 'POST', body: JSON.stringify({ company, role: title, portal_url: portalUrl }),
      });
      router.push(`/applications/${encodeURIComponent(data.application_id)}`);
    } catch (err) {
      setPrepareError(err instanceof Error ? err.message : 'Unable to prepare application.');
    } finally { setPreparing(false); }
  }

  async function handleGenerateTailoring() {
    setTailoring(true);
    try {
      await new Promise(r => setTimeout(r, 600));

      if (isIntern) {
        setTailoredResume(
          `TAILORED ENTRY-LEVEL RESUME PROPOSAL FOR ${company.toUpperCase()}\n\n` +
          `PROFESSIONAL OBJECTIVE:\n` +
          `Computer Science Graduate & Software Engineering Candidate seeking ${title} role. Proficient in Python, SQL, and core computer science fundamentals.\n\n` +
          `RELEVANT PROJECTS & COURSEWORK:\n` +
          `• Machine Learning & Data Systems Project (Python, PostgreSQL)\n` +
          `• Coursework: Data Structures, Algorithms, Operating Systems, Database Management\n\n` +
          `NOTE: Entry-level internship proposal emphasizes academic excellence and technical skills (No senior years required).`
        );
      } else {
        setTailoredResume(
          `TAILORED EXPERIENCED RESUME PROPOSAL FOR ${company.toUpperCase()}\n\n` +
          `PROFESSIONAL SUMMARY:\n` +
          `Engineered candidate specializing in ${title} roles with expertise in ${matchedKeywords.slice(0, 3).join(', ')}.\n\n` +
          `MATCHED KEYWORDS HIGHLIGHTED:\n` +
          `• Matched: ${matchedKeywords.join(', ')}\n` +
          `• Addressing Target Requirements: ${missingKeywords.join(', ')} (Example only — verify against your own experience)`
        );
      }
    } finally {
      setTailoring(false);
    }
  }

  return (
    <div className="space-y-6">
      <p role="note" className="rounded-lg border border-amber-800 bg-amber-950/30 p-4 text-sm text-amber-200">Preview assessment: scores, keywords, and resume text on this page are illustrative. They are not calculated from your uploaded resume. Review the employer listing before preparing an application.</p>
      {prepareError && <p role="alert" className="text-sm text-red-300">{prepareError}</p>}
      
      {/* Back Button */}
      <Link href="/jobs" className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 font-medium">
        <ArrowLeft size={14} /> Back to Jobs Feed
      </Link>

      {/* Header Info */}
      <div className="bg-neutral-900/60 p-6 rounded-2xl border border-neutral-800 space-y-3">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-white">{title}</h1>
            <div className="flex items-center gap-4 text-xs text-neutral-400 mt-1">
              <span className="flex items-center gap-1"><Building2 size={14} className="text-emerald-400" /> {company}</span>
              <span className="flex items-center gap-1"><MapPin size={14} className="text-neutral-500" /> India / Remote</span>
            </div>
          </div>

          <div className="text-right">
            <span className="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold flex items-center gap-1">
              <Target size={14} /> {matchScore}% Dynamic ATS Match
            </span>
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex items-center gap-3 pt-3 border-t border-neutral-800">
          <button
            onClick={handlePrepareApplication} disabled={preparing}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-emerald-900/30"
          >
            <Send size={14} /> Prepare Application & Route to Tracker
          </button>

          <button
            onClick={handleGenerateTailoring}
            className="px-4 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-semibold text-xs rounded-lg transition-all flex items-center gap-1.5 border border-neutral-700"
          >
            <Sparkles size={14} className="text-emerald-400" /> {tailoring ? 'Generating Proposal...' : 'AI Resume Suggestion'}
          </button>
        </div>
      </div>

      {/* Grid: Keyword Match Breakdown & Job Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* ATS Keyword Breakdown Sidebar */}
        <div className="md:col-span-1 bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 space-y-4">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
            <Target size={14} className="text-emerald-400" /> ATS Keyword Breakdown
          </h2>

          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
              <CheckCircle2 size={12} /> Matched Keywords ({matchedKeywords.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {matchedKeywords.map((kw, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800 text-[10px] font-medium">
                  {kw}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-neutral-800">
            <span className="text-[11px] font-semibold text-rose-400 flex items-center gap-1">
              <XCircle size={12} /> Missing Keywords ({missingKeywords.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {missingKeywords.map((kw, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-800 text-[10px] font-medium">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Tailored Resume Proposal & Job Description */}
        <div className="md:col-span-2 space-y-6">
          
          {/* AI Tailored Resume Suggestion Proposal */}
          {tailoredResume && (
            <div className="bg-neutral-900/80 p-5 rounded-xl border border-emerald-800 space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <Sparkles size={14} /> TruthGuard Role-Specific Resume Proposal
                </h3>
                <span className="text-[10px] text-neutral-400">Awaiting candidate review</span>
              </div>
              <pre className="p-4 bg-neutral-950 rounded-lg text-xs font-mono text-neutral-200 whitespace-pre-wrap leading-relaxed border border-neutral-800">
                {tailoredResume}
              </pre>
            </div>
          )}

          {/* Job Description Text */}
          <div className="bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Job Description & Responsibilities</h3>
            <div className="text-xs text-neutral-300 leading-relaxed space-y-2 font-sans">
              <p>Position: <strong>{title}</strong> at <strong>{company}</strong>.</p>
              <p><strong>Responsibilities & Requirements:</strong></p>
              <ul className="list-disc pl-5 space-y-1 text-neutral-400">
                {isIntern ? (
                  <>
                    <li>Assist engineering teams in developing software components and feature modules.</li>
                    <li>Write clean, tested Python code and participate in code reviews.</li>
                    <li>Learn production CI/CD, Git workflows, and API architectures.</li>
                  </>
                ) : isSecurity ? (
                  <>
                    <li>Conduct vulnerability assessments and security code audits across microservices.</li>
                    <li>Implement authentication, authorization, and data encryption standards.</li>
                    <li>Collaborate with DevOps to enforce zero-trust infrastructure policies.</li>
                  </>
                ) : (
                  <>
                    <li>Design, build, and maintain scalable data pipelines and web services.</li>
                    <li>Optimize database schema, index performance, and asynchronous tasks.</li>
                    <li>Participate in system design, unit testing, and technical documentation.</li>
                  </>
                )}
              </ul>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
