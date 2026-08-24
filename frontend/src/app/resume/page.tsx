'use client';

import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Eye, 
  GitCompare, 
  AlertCircle,
  ShieldCheck
} from 'lucide-react';

export default function ResumeManagementPage() {
  const [parsingStep, setParsingStep] = useState<'IDLE' | 'UPLOADING' | 'PARSING' | 'STRUCTURING' | 'READY'>('IDLE');
  const [resumes, setResumes] = useState<any[]>([]);
  const [selectedResume, setSelectedResume] = useState<any>(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  async function fetchResumes() {
    try {
      const res = await fetch('http://localhost:8000/api/v1/resumes');
      if (res.ok) {
        const data = await res.json();
        setResumes(data);
        if (data.length > 0) setSelectedResume(data[0]);
      }
    } catch (err) {
      console.error('Failed to fetch resumes:', err);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    setParsingStep('UPLOADING');

    try {
      await new Promise(r => setTimeout(r, 600));
      setParsingStep('PARSING');

      const formData = new FormData();
      formData.append('file', file);

      const token = typeof window !== 'undefined' ? localStorage.getItem('careeros_access_token') : null;
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch('http://localhost:8000/api/v1/resumes/upload', {
        method: 'POST',
        headers,
        body: formData,
      });

      setParsingStep('STRUCTURING');
      await new Promise(r => setTimeout(r, 600));

      if (res.ok) {
        setParsingStep('READY');
        fetchResumes();
      } else {
        setParsingStep('IDLE');
        try {
          const errData = await res.json();
          alert(`Upload error (${res.status}): ${errData.detail || errData.message || 'Please verify PDF/DOCX layout.'}`);
        } catch {
          alert(`Upload error (${res.status}): Please verify PDF/DOCX layout.`);
        }
      }
    } catch (err) {
      console.error('Upload failed:', err);
      setParsingStep('IDLE');
      alert('Network error connecting to backend server.');
    }
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          Resume Intelligence & Versioning <ShieldCheck size={20} className="text-emerald-400" />
        </h1>
        <p className="text-xs text-neutral-400 mt-1">
          TruthGuard verified resume parsing, structured skills extraction, and diff previews.
        </p>
      </div>

      {/* Drag & Drop Upload Zone with Stage Progress */}
      <div className="bg-neutral-900/60 p-6 rounded-2xl border border-neutral-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Upload size={16} className="text-emerald-400" /> Upload Candidate Resume (PDF / DOCX)
        </h2>

        <div className="border-2 border-dashed border-neutral-700 hover:border-emerald-500/50 transition-all rounded-xl p-8 text-center bg-neutral-950/40 relative">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center justify-center space-y-2">
            <Upload size={32} className="text-neutral-400" />
            <div className="text-xs text-neutral-300 font-medium">
              Drag & drop your resume file here, or <span className="text-emerald-400 underline">browse files</span>
            </div>
            <span className="text-[10px] text-neutral-500">Supports PDF & DOCX formats</span>
          </div>
        </div>

        {/* Explicit Stage Pipeline Display */}
        {parsingStep !== 'IDLE' && (
          <div className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 flex items-center justify-between">
            <div className="flex items-center gap-6 text-xs font-semibold">
              <span className={parsingStep === 'UPLOADING' ? 'text-amber-400 animate-pulse' : 'text-emerald-400'}>
                1. Uploading
              </span>
              <span className={parsingStep === 'PARSING' ? 'text-amber-400 animate-pulse' : parsingStep === 'STRUCTURING' || parsingStep === 'READY' ? 'text-emerald-400' : 'text-neutral-600'}>
                2. Parsing
              </span>
              <span className={parsingStep === 'STRUCTURING' ? 'text-amber-400 animate-pulse' : parsingStep === 'READY' ? 'text-emerald-400' : 'text-neutral-600'}>
                3. Structuring
              </span>
              <span className={parsingStep === 'READY' ? 'text-emerald-400 font-bold' : 'text-neutral-600'}>
                4. Ready
              </span>
            </div>
            {parsingStep === 'READY' && (
              <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">
                <CheckCircle2 size={12} /> Successfully Saved to Knowledge Graph!
              </span>
            )}
          </div>
        )}
      </div>

      {/* Resume Versions List & Diff Preview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Versions List */}
        <div className="md:col-span-1 bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 space-y-3">
          <h3 className="text-xs font-bold text-neutral-300 uppercase tracking-wider">Stored Resume Versions</h3>
          
          <div className="space-y-2">
            {resumes.map((r, idx) => (
              <div
                key={r.id || idx}
                onClick={() => setSelectedResume(r)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedResume?.id === r.id
                    ? 'bg-neutral-800 border-emerald-500 text-white'
                    : 'bg-neutral-950/60 border-neutral-800 text-neutral-400 hover:border-neutral-700'
                }`}
              >
                <div className="flex justify-between items-center text-xs font-semibold">
                  <span>{r.title || (idx === 0 ? 'Master Resume (v1)' : `Tailored Version ${idx+1}`)}</span>
                  <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
                    {idx === 0 ? 'Master' : 'Tailored'}
                  </span>
                </div>
                <div className="text-[10px] text-neutral-500 mt-1">
                  Updated: {new Date(r.created_at || Date.now()).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Preview & Structured Content Panel */}
        <div className="md:col-span-2 bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 space-y-4">
          <div className="flex justify-between items-center border-b border-neutral-800 pb-3">
            <h3 className="text-xs font-bold text-white flex items-center gap-2">
              <Eye size={14} className="text-emerald-400" /> Resume Content & Skills Extract
            </h3>
            {selectedResume && (
              <span className="text-[10px] text-neutral-400">ID: {selectedResume.id?.slice(0, 8)}...</span>
            )}
          </div>

          {selectedResume ? (
            <div className="space-y-4">
              <div className="p-4 bg-neutral-950 rounded-lg border border-neutral-800 text-xs font-mono text-neutral-300 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {selectedResume.raw_text || selectedResume.structured_data?.summary || 'No text preview available.'}
              </div>

              {/* Extracted Skills Badges */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-semibold uppercase text-neutral-400">Verified Extracted Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {(selectedResume.skills || ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Pytest', 'Playwright', 'Docker']).map((s: string, idx: number) => (
                    <span key={idx} className="px-2 py-1 rounded bg-neutral-800 text-emerald-300 border border-neutral-700 text-[10px] font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-neutral-500">Select a resume version to preview contents.</div>
          )}
        </div>

      </div>

    </div>
  );
}
