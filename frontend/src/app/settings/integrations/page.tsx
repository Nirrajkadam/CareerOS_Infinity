'use client';

import { apiRequest } from '../../../lib/apiClient';

import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  ToggleLeft, 
  ToggleRight,
  ShieldCheck,
  Activity
} from 'lucide-react';

export default function SourceIntegrationsPage() {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSourceHealth();
  }, []);

  async function fetchSourceHealth() {
    try {
      const res = await apiRequest('/api/v1/jobs/source-health');
      if (res.ok) {
        const data = await res.json();
        setSources(data.map((s: any) => ({ ...s, enabled: true })));
      }
    } catch (err) {
      console.error('Failed to fetch source health:', err);
    } finally {
      setLoading(false);
    }
  }

  function toggleSource(id: string) {
    setSources(prev => prev.map(s => s.id === id ? { ...s, enabled: !s.enabled } : s));
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          Job Source Health & Integrations <Sliders size={20} className="text-emerald-400" />
        </h1>
        <p className="text-xs text-neutral-400 mt-1">
          Authentic live backend health telemetry. Official APIs are marked Stable; candidate browser sources are marked Best-Effort.
        </p>
      </div>

      {/* Sources List Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-8 text-center text-xs text-neutral-500">Querying backend source health telemetry...</div>
        ) : (
          sources.map((src) => (
            <div key={src.id} className="bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 flex justify-between items-center">
              <div className="space-y-1.5">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-bold text-white">{src.name}</h3>
                  <span className="px-2.5 py-0.5 rounded-full bg-neutral-950 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
                    {src.badge}
                  </span>
                </div>
                
                <div className="text-xs text-neutral-400 flex items-center gap-4">
                  <span>Category: {src.category}</span>
                  <span>Reliability: {src.reliability}</span>
                </div>
              </div>

              {/* Toggle Button */}
              <button
                onClick={() => toggleSource(src.id)}
                className="text-neutral-400 hover:text-white transition"
              >
                {src.enabled ? (
                  <ToggleRight size={32} className="text-emerald-500" />
                ) : (
                  <ToggleLeft size={32} className="text-neutral-600" />
                )}
              </button>
            </div>
          ))
        )}
      </div>

    </div>
  );
}
