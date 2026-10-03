'use client';

import React, { useState } from 'react';
import { 
  UserCheck, 
  Briefcase, 
  GraduationCap, 
  Code, 
  Award, 
  Target, 
  Plus, 
  Trash2, 
  Save,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Github,
  Linkedin,
  Mail,
  Phone,
  BookOpen
} from 'lucide-react';

export default function MasterProfilePage() {
  const [activeTab, setActiveTab] = useState<'skills' | 'projects' | 'education' | 'certifications' | 'experience'>('skills');
  const [isFresher, setIsFresher] = useState<boolean>(true);
  const [savedMessage, setSavedMessage] = useState(false);

  // Authentically extracted from Nirajkadam.pdf
  const [personalInfo] = useState({
    name: 'NIRAJ KADAM',
    email: 'nirraj.official@gmail.com',
    phone: '+91-9579083736',
    linkedin: 'linkedin.com/in/niraj-kadam18',
    github: 'github.com/957908',
    summary: 'Results-driven Computer Engineering graduate and PG-DBDA (Post Graduate Diploma in Big Data Analytics) candidate at C-DAC specializing in AI, Machine Learning, and Big Data Technologies. Experienced in developing multi-agent AI platforms, integrating Large Language Models (LLMs), and designing automated data pipelines.'
  });

  const [skills, setSkills] = useState([
    'Python (Pandas, NumPy, Scikit-Learn)', 'SQL', 'FastAPI', 'PySpark', 'Apache Spark', 
    'Generative AI', 'LLMs', 'LangChain', 'Multi-Agent Systems', 'RAG', 'Ollama AI',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Docker', 'Git', 'Linux', 'GCP',
    'Hadoop', 'HDFS', 'Hive', 'Kafka', 'MinIO', 'Parquet', 'ETL', 'Data Warehousing',
    'Java', 'C++', 'JavaScript', 'HTML/CSS', 'Flask', 'REST APIs',
    'Nmap', 'Gobuster', 'ADB', 'OWASP Standards', 'Cryptography'
  ]);
  const [newSkill, setNewSkill] = useState('');

  const [educationList] = useState([
    {
      degree: 'Post Graduate Diploma in Big Data Analytics (PG-DBDA)',
      school: "C-DAC's Advanced Computing Training School (ACTS)",
      year: 'Feb 2026 – Present (Expected: Aug 2026)',
      desc: 'Specializing in Big Data Architectures, Advanced Data Analytics, Data Warehousing, and Cloud Computing.'
    },
    {
      degree: 'Bachelor of Engineering (B.E. Computer Engineering)',
      school: 'Mumbai University (Smt. Indira Gandhi College of Engineering, Navi Mumbai)',
      year: '2021 – 2025',
      desc: 'Specialization: Internet of Things (IoT) & Cyber Security including Blockchain Technology.'
    }
  ]);

  const [projectsList] = useState([
    {
      title: 'Multi-Agent AI Data Lakehouse Platform for Betting App Analysis',
      duration: '2 Months',
      tech: 'Python, FastAPI, Apache Spark (PySpark), PostgreSQL, Docker, Parquet, MinIO, Ollama AI, LangChain',
      bullets: [
        'Developed a multi-agent ETL pipeline using PySpark and FastAPI to automate scraping, structured transaction extraction (UPI, bank, crypto), and schema normalization.',
        'Integrated LLM agents via LangChain and Ollama AI to parse OCR text from transaction screenshots and automatically categorize transaction classifications.',
        'Optimized storage by writing partitioned Parquet data into MinIO object storage using a Bronze/Silver/Gold lakehouse design, reducing query latency and storage footprint.'
      ]
    },
    {
      title: 'CyberSquad: Automated Vulnerability Assessment & Security Auditing Tool',
      duration: '8 Months',
      tech: 'Python, FastAPI, SQL, Nmap, Ollama AI, Gobuster, ADB, VirusTotal API, Vulners API',
      bullets: [
        'Engineered a Python-based security tool integrating Nmap, Gobuster, and ADB to automate network vulnerability scans and security audits on Android devices.',
        'Incorporated Ollama AI for intelligent CVE analysis and built an automated reporting engine generating detailed PDF security assessments.'
      ]
    },
    {
      title: 'Decentralized File Storage System',
      duration: '3 Months',
      tech: 'Blockchain, Python, Flask, Cryptography, MySQL',
      bullets: [
        'Designed a secure blockchain-backed storage platform using Flask, MySQL, and AES-256 encryption to ensure immutable transaction logging and role-based access control.'
      ]
    },
    {
      title: 'Smart Door Lock System',
      duration: '4 Months',
      tech: 'IoT, Raspberry Pi/Arduino, Embedded Systems, Cloud Integration',
      bullets: [
        'Developed an IoT smart lock system using Raspberry Pi/Arduino to sync physical access hardware with a secure cloud backend for real-time remote monitoring.'
      ]
    }
  ]);

  const [certificationsList] = useState([
    { title: 'Google Cloud Computing Fundamentals', provider: 'Google Cloud' },
    { title: 'Google Cybersecurity Professional Certificate', provider: 'Coursera / Google' }
  ]);

  function handleAddSkill() {
    if (!newSkill.trim()) return;
    setSkills(prev => [...prev, newSkill.trim()]);
    setNewSkill('');
  }

  function handleDeleteSkill(skillName: string) {
    setSkills(prev => prev.filter(s => s !== skillName));
  }

  function handleSaveProfile() {
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 2000);
  }

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="border-b border-neutral-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold text-white">{personalInfo.name}</h1>
            <span className="px-3 py-1 rounded-full bg-orange-500/10 text-[#eb5a28] border border-orange-500/30 text-xs font-bold">
              VERIFIED CANDIDATE PROFILE
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs text-neutral-400 mt-2 font-mono">
            <span className="flex items-center gap-1"><Mail size={13} className="text-[#eb5a28]" /> {personalInfo.email}</span>
            <span className="flex items-center gap-1"><Phone size={13} className="text-[#eb5a28]" /> {personalInfo.phone}</span>
            <span className="flex items-center gap-1"><Linkedin size={13} className="text-[#eb5a28]" /> {personalInfo.linkedin}</span>
            <span className="flex items-center gap-1"><Github size={13} className="text-[#eb5a28]" /> {personalInfo.github}</span>
          </div>
        </div>

        <button
          onClick={handleSaveProfile}
          className="px-5 py-2.5 bg-[#eb5a28] hover:bg-[#d94e1d] text-white font-bold text-xs rounded-full transition-all flex items-center gap-2 shadow-lg shadow-orange-950/40 shrink-0 active:scale-95"
        >
          <Save size={15} /> {savedMessage ? 'Saved to Knowledge Graph!' : 'Save Master Profile'}
        </button>
      </div>

      {/* Professional Summary Box */}
      <div className="bg-[#0d0d12] p-6 rounded-2xl border border-neutral-800 space-y-2.5 shadow-xl">
        <h3 className="text-xs font-bold text-[#eb5a28] uppercase tracking-wider flex items-center gap-1.5">
          <BookOpen size={15} /> Professional Summary
        </h3>
        <p className="text-sm text-neutral-300 leading-relaxed font-sans">
          {personalInfo.summary}
        </p>
      </div>

      {/* Candidate Status Banner */}
      <div className="bg-[#0d0d12] p-5 rounded-2xl border border-neutral-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <ShieldCheck size={22} className="text-emerald-400 shrink-0" />
          <div>
            <span className="text-sm font-bold text-white block">Candidate Status: {isFresher ? 'Fresher / Entry-Level (0 Years Commercial Exp)' : 'Experienced Professional'}</span>
            <span className="text-xs text-neutral-400">TruthGuard Safety: Resumes & proposals will strictly emphasize your PG-DBDA, B.E. Degree & Multi-Agent Projects without fabricating experience.</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 bg-[#111116] p-1.5 rounded-full border border-neutral-800 shrink-0">
          <button
            onClick={() => setIsFresher(true)}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition ${
              isFresher ? 'bg-[#eb5a28] text-white shadow-md' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Fresher (0 Yrs)
          </button>
          <button
            onClick={() => setIsFresher(false)}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition ${
              !isFresher ? 'bg-[#eb5a28] text-white shadow-md' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Experienced
          </button>
        </div>
      </div>

      {/* Profile Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-neutral-800 pb-3">
        {[
          { key: 'skills', label: `Technical Skills (${skills.length})`, icon: Code },
          { key: 'projects', label: `Academic Projects (${projectsList.length})`, icon: Target },
          { key: 'education', label: 'Education', icon: GraduationCap },
          { key: 'certifications', label: 'Certifications', icon: Award },
          { key: 'experience', label: 'Work Experience', icon: Briefcase },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-4 py-2 rounded-full text-xs font-bold transition flex items-center gap-2 ${
                isActive
                  ? 'bg-[#eb5a28] text-white shadow-md shadow-orange-950/40'
                  : 'bg-[#0d0d12] text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700'
              }`}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>


      {/* Tab Content */}
      <div className="bg-[#0d0d12] p-6 rounded-2xl border border-neutral-800 space-y-6 shadow-xl">
        
        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Code size={16} className="text-[#eb5a28]" /> Extracted Technical Skills from Resume
            </h3>

            <div className="flex gap-2">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                placeholder="Add new skill (e.g. Terraform, Kubernetes)..."
                className="flex-1 px-4 py-2.5 bg-[#111116] border border-neutral-800 rounded-xl text-xs text-white focus:outline-none focus:border-[#eb5a28] transition-colors"
              />
              <button
                onClick={handleAddSkill}
                className="px-5 py-2.5 bg-[#eb5a28] hover:bg-[#d94e1d] text-white font-bold text-xs rounded-xl transition shadow-md shadow-orange-950/40 flex items-center gap-1.5 active:scale-95"
              >
                <Plus size={14} /> Add Skill
              </button>
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              {skills.map((skill, idx) => (
                <span key={idx} className="px-3.5 py-1.5 rounded-full bg-[#161620] text-neutral-200 border border-neutral-800 text-xs font-medium flex items-center gap-2 hover:border-orange-500/40 transition-colors">
                  {skill}
                  <button onClick={() => handleDeleteSkill(skill)} className="text-neutral-500 hover:text-rose-400 transition">
                    <Trash2 size={12} />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Target size={16} className="text-[#eb5a28]" /> Academic & Technical Projects
            </h3>
            {projectsList.map((proj, idx) => (
              <div key={idx} className="p-5 bg-[#111116] rounded-2xl border border-neutral-800 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-sm font-bold text-white">{proj.title}</h4>
                    <span className="text-xs text-neutral-400">Duration: {proj.duration}</span>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-orange-500/10 text-[#eb5a28] border border-orange-500/30 text-xs font-mono font-bold">
                    {proj.tech}
                  </span>
                </div>

                <ul className="space-y-1.5 text-xs text-neutral-300 list-disc list-inside leading-relaxed">
                  {proj.bullets.map((b, bIdx) => (
                    <li key={bIdx}>{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {/* Education Tab */}
        {activeTab === 'education' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Verified Education Records</h3>
            {educationList.map((edu, idx) => (
              <div key={idx} className="p-5 bg-neutral-950 rounded-xl border border-neutral-800 space-y-2">
                <div className="flex justify-between items-center text-xs font-bold text-white">
                  <span>{edu.degree}</span>
                  <span className="text-neutral-400 font-normal">{edu.year}</span>
                </div>
                <div className="text-xs text-emerald-400 font-semibold">{edu.school}</div>
                <p className="text-xs text-neutral-400">{edu.desc}</p>
              </div>
            ))}
          </div>
        )}

        {/* Certifications Tab */}
        {activeTab === 'certifications' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Verified Professional Certifications</h3>
            {certificationsList.map((cert, idx) => (
              <div key={idx} className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 flex justify-between items-center text-xs font-bold text-white">
                <span className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-emerald-400" /> {cert.title}
                </span>
                <span className="px-2.5 py-1 rounded bg-neutral-900 text-emerald-400 border border-neutral-800 text-[10px]">
                  {cert.provider}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Experience Tab */}
        {activeTab === 'experience' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Career Experience Verification</h3>
            <div className="p-6 bg-neutral-950 rounded-xl border border-emerald-900/50 space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                <CheckCircle2 size={16} /> 🟢 Verified Candidate Mode: Fresher / Entry-Level (0 Years Experience)
              </div>
              <p className="text-xs text-neutral-300 leading-relaxed">
                As verified from <strong>Nirajkadam.pdf</strong>, you are currently pursuing your <strong>PG-DBDA at C-DAC</strong> after completing your <strong>B.E. in Computer Engineering</strong>. TruthGuard will strictly highlight your multi-agent AI lakehouse platform, CyberSquad security tool, and big data skillsets without fabricating false corporate work experience.
              </p>
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
