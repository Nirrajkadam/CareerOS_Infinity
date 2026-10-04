'use client'

import React, { useState } from 'react';
import { MessageSquare, Sparkles, Brain, Target, ChevronDown, Mic, ChevronUp } from 'lucide-react';
import { API_BASE_URL } from '@/lib/apiClient';

const MOCK_QUESTIONS = [
  {
    id: 1,
    category: 'Behavioral',
    question: 'Tell me about a time you had to lead a project with limited resources. How did you ensure its success?',
    tips: [
      'Use the STAR method (Situation, Task, Action, Result)',
      'Focus on your specific leadership actions',
      'Quantify the results if possible'
    ]
  },
  {
    id: 2,
    category: 'Technical',
    question: 'Explain the difference between server-side rendering (SSR) and client-side rendering (CSR). When would you use each?',
    tips: [
      'Mention SEO implications for SSR',
      'Discuss initial load time vs interactive performance',
      'Give examples of frameworks that support these rendering patterns'
    ]
  },
  {
    id: 3,
    category: 'Situational',
    question: 'You discover a critical bug in production right before a major product launch. What are your immediate steps?',
    tips: [
      'Prioritize communication with stakeholders',
      'Discuss risk assessment (delay launch vs hotfix)',
      'Explain your debugging and root cause analysis process'
    ]
  },
  {
    id: 4,
    category: 'Behavioral',
    question: 'Describe a situation where you strongly disagreed with a team member or manager. How did you resolve the conflict?',
    tips: [
      'Emphasize active listening and empathy',
      'Focus on finding a data-driven or compromise solution',
      'Keep the tone professional and objective'
    ]
  },
  {
    id: 5,
    category: 'Technical',
    question: 'How do you approach optimizing a slow-performing web application?',
    tips: [
      'Mention profiling tools (e.g., Chrome DevTools, Lighthouse)',
      'Discuss asset optimization, caching, and lazy loading',
      'Talk about database query optimization if applicable'
    ]
  },
  {
    id: 6,
    category: 'Situational',
    question: 'You are assigned a task with a technology stack you have never used before. How do you approach it?',
    tips: [
      'Demonstrate a growth mindset and willingness to learn',
      'Outline your strategy for reading documentation and finding resources',
      'Mention how you would leverage team knowledge or pair programming'
    ]
  }
];

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'Behavioral': return 'text-blue-400 border-blue-400/30 bg-blue-400/10';
    case 'Technical': return 'text-purple-400 border-purple-400/30 bg-purple-400/10';
    case 'Situational': return 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10';
    default: return 'text-gray-400 border-gray-400/30 bg-gray-400/10';
  }
};

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'Behavioral': return <Brain className="w-4 h-4 mr-2" />;
    case 'Technical': return <Target className="w-4 h-4 mr-2" />;
    case 'Situational': return <MessageSquare className="w-4 h-4 mr-2" />;
    default: return null;
  }
};

export default function InterviewPrepPage() {
  const [jobDescription, setJobDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [questions, setQuestions] = useState<typeof MOCK_QUESTIONS>([]);
  const [expandedQuestionId, setExpandedQuestionId] = useState<number | null>(null);

  const handleGenerate = () => {
    if (!jobDescription.trim()) return;
    setIsGenerating(true);
    // Simulate API call
    setTimeout(() => {
      setQuestions(MOCK_QUESTIONS);
      setIsGenerating(false);
    }, 1500);
  };

  const toggleTips = (id: number) => {
    setExpandedQuestionId(expandedQuestionId === id ? null : id);
  };

  return (
    <div className="min-h-screen bg-[#070709] text-white p-6 md:p-12 font-sans">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            Interview Prep <span className="text-[#eb5a28]">Studio</span>
          </h1>
          <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
            Master your next interview with AI-powered mock questions tailored exactly to your target role.
          </p>
        </div>

        {/* Generate Questions Section */}
        <div className="bg-[#0d0d12] border border-neutral-800 rounded-2xl p-6 md:p-8 shadow-xl">
          <div className="flex items-center space-x-3 mb-6">
            <Sparkles className="text-[#eb5a28] w-6 h-6" />
            <h2 className="text-2xl font-semibold">Generate Questions</h2>
          </div>
          
          <div className="space-y-4">
            <label className="block text-sm font-medium text-neutral-400">
              Paste the Job Description
            </label>
            <textarea
              className="w-full bg-[#111116] border border-neutral-800 rounded-xl p-4 text-neutral-200 focus:outline-none focus:border-[#eb5a28] focus:ring-1 focus:ring-[#eb5a28] transition-all h-40 resize-y"
              placeholder="E.g. We are looking for a Senior Frontend Engineer with deep knowledge of React, Next.js, and TypeScript..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
            <div className="flex justify-end">
              <button
                onClick={handleGenerate}
                disabled={!jobDescription.trim() || isGenerating}
                className="flex items-center space-x-2 bg-[#eb5a28] hover:bg-[#d44c1e] text-white px-6 py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Interview Questions</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Generated Questions */}
        {questions.length > 0 && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold px-2">Tailored Questions for You</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {questions.map((q) => (
                <div key={q.id} className="bg-[#0d0d12] border border-neutral-800 rounded-2xl overflow-hidden shadow-xl flex flex-col">
                  <div className="p-6 flex-grow space-y-4">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(q.category)}`}>
                      {getCategoryIcon(q.category)}
                      {q.category}
                    </div>
                    <h4 className="text-lg leading-relaxed text-neutral-200">
                      {q.question}
                    </h4>
                  </div>
                  
                  {/* Tips Section */}
                  <div className="border-t border-neutral-800 bg-[#111116]">
                    <button 
                      onClick={() => toggleTips(q.id)}
                      className="w-full flex items-center justify-between p-4 text-sm font-medium text-neutral-400 hover:text-neutral-200 transition-colors"
                    >
                      <span className="flex items-center">
                        <Brain className="w-4 h-4 mr-2" />
                        How to answer
                      </span>
                      {expandedQuestionId === q.id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                    
                    {expandedQuestionId === q.id && (
                      <div className="px-6 pb-6 pt-2">
                        <ul className="space-y-2">
                          {q.tips.map((tip, idx) => (
                            <li key={idx} className="flex items-start text-sm text-neutral-400">
                              <span className="text-[#eb5a28] mr-2 mt-0.5">•</span>
                              {tip}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Practice Mode */}
        <div className="bg-gradient-to-br from-[#0d0d12] to-[#111116] border border-neutral-800 rounded-2xl p-8 shadow-xl text-center flex flex-col items-center space-y-6">
          <div className="w-16 h-16 bg-[#eb5a28]/10 rounded-full flex items-center justify-center border border-[#eb5a28]/20">
            <Mic className="w-8 h-8 text-[#eb5a28]" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold">Live Practice Session</h2>
            <p className="text-neutral-400 max-w-md mx-auto">
              Simulate a real interview environment with our AI voice interviewer. Practice your responses and get instant feedback.
            </p>
          </div>
          <button
            disabled
            className="flex items-center space-x-2 bg-neutral-800 text-neutral-400 px-8 py-4 rounded-xl font-medium cursor-not-allowed border border-neutral-700"
          >
            <Mic className="w-5 h-5" />
            <span>Start Practice Mode</span>
            <span className="bg-neutral-900 px-2 py-1 rounded text-xs ml-2">Coming Soon</span>
          </button>
        </div>
      </div>
    </div>
  );
}
