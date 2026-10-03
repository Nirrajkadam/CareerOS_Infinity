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

import { API_BASE_URL } from '@/lib/apiClient';

export default function ResumeManagementPage() {
  const [parsingStep, setParsingStep] = useState<'IDLE' | 'UPLOADING' | 'PARSING' | 'STRUCTURING' | 'READY'>('IDLE');
  const [resumes, setResumes] = useState<any[]>([]);
  const [selectedResume, setSelectedResume] = useState<any>(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  async function fetchResumes() {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('careeros_access_token') : null;
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const res = await fetch(`${API_BASE_URL}/api/v1/resumes`, { headers });
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

      const res = await fetch(`${API_BASE_URL}/api/v1/resumes/upload`, {
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
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-2 border bg-orange-500/10 border-orange-500/30 text-[#eb5a28]">
          <FileText size={13} />
          <span>RESUME INTELLIGENCE</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Resume Intelligence & Versioning <ShieldCheck size={24} className="text-emerald-400" />
        </h1>
        <p className="text-sm text-neutral-400 mt-1">
          TruthGuard verified resume parsing, structured skills extraction, and diff previews.
        </p>
      </div>

      {/* Drag & Drop Upload Zone with Stage Progress */}
      <div className="bg-[#0d0d12] p-6 rounded-2xl border border-neutral-800 space-y-4 shadow-xl">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Upload size={16} className="text-[#eb5a28]" /> Upload Candidate Resume (PDF / DOCX)
        </h2>

        <div className="border-2 border-dashed border-neutral-800 hover:border-[#eb5a28]/60 transition-all rounded-2xl p-10 text-center bg-[#111116]/80 relative group">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-orange-500/15 text-[#eb5a28] flex items-center justify-center group-hover:scale-110 transition-transform">
              <Upload size={24} />
            </div>
            <div className="text-sm text-neutral-300 font-medium">
              Drag & drop your resume file here, or <span className="text-[#eb5a28] underline font-bold">browse files</span>
            </div>
            <span className="text-xs text-neutral-500">Supports PDF & DOCX formats</span>
          </div>
        </div>

        {/* Explicit Stage Pipeline Display */}
        {parsingStep !== 'IDLE' && (
          <div className="p-4 bg-[#111116] rounded-xl border border-neutral-800 flex items-center justify-between">
            <div className="flex items-center gap-6 text-xs font-semibold">
              <span className={parsingStep === 'UPLOADING' ? 'text-[#eb5a28] animate-pulse font-bold' : 'text-emerald-400'}>
                1. Uploading
              </span>
              <span className={parsingStep === 'PARSING' ? 'text-[#eb5a28] animate-pulse font-bold' : parsingStep === 'STRUCTURING' || parsingStep === 'READY' ? 'text-emerald-400' : 'text-neutral-600'}>
                2. Parsing
              </span>
              <span className={parsingStep === 'STRUCTURING' ? 'text-[#eb5a28] animate-pulse font-bold' : parsingStep === 'READY' ? 'text-emerald-400' : 'text-neutral-600'}>
                3. Structuring
              </span>
              <span className={parsingStep === 'READY' ? 'text-emerald-400 font-bold' : 'text-neutral-600'}>
                4. Ready
              </span>
            </div>
            {parsingStep === 'READY' && (
              <span className="text-xs text-emerald-400 font-bold flex items-center gap-1">
                <CheckCircle2 size={14} /> Successfully Saved to Knowledge Graph!
              </span>
            )}
          </div>
        )}
      </div>

      {/* Resume Versions List & Diff Preview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Versions List */}
        <div className="md:col-span-1 bg-[#0d0d12] p-5 rounded-2xl border border-neutral-800 space-y-4 shadow-xl">
          <h3 className="text-xs font-bold text-neutral-300 uppercase tracking-wider">Stored Resume Versions</h3>
          
          <div className="space-y-2.5">
            {resumes.map((r, idx) => (
              <div
                key={r.id || idx}
                onClick={() => setSelectedResume(r)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                  selectedResume?.id === r.id
                    ? 'bg-[#181822] border-[#eb5a28] text-white shadow-md'
                    : 'bg-[#111116] border-neutral-800 text-neutral-400 hover:border-neutral-700'
                }`}
              >
                <div className="flex justify-between items-center text-xs font-bold">
                  <span className={selectedResume?.id === r.id ? 'text-[#eb5a28]' : 'text-white'}>
                    {r.title || (idx === 0 ? 'Master Resume (v1)' : `Tailored Version ${idx+1}`)}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-500/10 text-[#eb5a28] border border-orange-500/30 font-extrabold">
                    {idx === 0 ? 'Master' : 'Tailored'}
                  </span>
                </div>
                <div className="text-[11px] text-neutral-500 mt-1.5">
                  Updated: {new Date(r.created_at || Date.now()).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Preview & Structured Content Panel */}
        <div className="md:col-span-2 bg-[#0d0d12] p-6 rounded-2xl border border-neutral-800 space-y-4 shadow-xl">
          <div className="flex justify-between items-center border-b border-neutral-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Eye size={16} className="text-[#eb5a28]" /> Resume Content & Skills Extract
            </h3>
            {selectedResume && (
              <span className="text-xs text-neutral-500 font-mono">ID: {selectedResume.id?.slice(0, 8)}...</span>
            )}
          </div>

          {selectedResume ? (
            <div className="space-y-4">
              <div className="p-5 bg-[#070709] rounded-xl border border-neutral-850 text-xs font-mono text-neutral-300 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {selectedResume.raw_text || selectedResume.structured_data?.summary || 'No text preview available.'}
              </div>

              {/* Extracted Skills Badges */}
              <div className="space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Verified Extracted Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {(selectedResume.skills || ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Pytest', 'Playwright', 'Docker']).map((s: string, idx: number) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg bg-[#161620] text-neutral-200 border border-neutral-800 text-xs font-medium hover:border-orange-500/40 transition-colors">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="py-16 text-center text-sm text-neutral-500">Select a resume version to preview contents.</div>
          )}
        </div>

      </div>

    </div>
  );
}
