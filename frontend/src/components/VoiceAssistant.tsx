'use client';
import React, { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Bot, Mic, MicOff, Send, Square, Volume2, X } from 'lucide-react';
import { apiFetch, apiRequest } from '../lib/apiClient';
import { AssistantLanguage, chooseIndianVoice, recognitionText, safeAssistantPath } from '../lib/assistant';

type Step = { action: string; status: 'completed' | 'failed'; summary: string };
type Reply = { reply: string; mode: string; steps: Step[]; links: { label: string; url: string }[]; navigate_url?: string };
type Message = { role: 'user' | 'assistant'; content: string; result?: Reply };
type Config = { ai_configured: boolean; neural_voice_configured: boolean };
type RecognitionResult = { isFinal: boolean; 0: { transcript: string } };
type Recognition = {
  lang: string; continuous: boolean; interimResults: boolean;
  onstart: (() => void) | null; onend: (() => void) | null;
  onresult: ((event: { results: ArrayLike<RecognitionResult> }) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  start(): void; abort(): void;
};
type SpeechWindow = Window & { SpeechRecognition?: new () => Recognition; webkitSpeechRecognition?: new () => Recognition };
const welcome: Message = { role: 'assistant', content: 'Namaste! I’m KAI, your AI career assistant. Tell me your goal. I can search stored jobs, compare your profile and prepare application records for you.' };

export default function VoiceAssistant() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([welcome]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState<AssistantLanguage>('en-IN');
  const [config, setConfig] = useState<Config | null>(null);
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [readAloud, setReadAloud] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [notice, setNotice] = useState('');
  const [voiceLabel, setVoiceLabel] = useState('Device voice');
  const recognition = useRef<Recognition | null>(null);
  const audio = useRef<HTMLAudioElement | null>(null);
  const audioUrl = useRef<string | null>(null);
  const speechAbort = useRef<AbortController | null>(null);
  const chatAbort = useRef<AbortController | null>(null);
  const speechVersion = useRef(0);
  const busyRef = useRef(false);
  const alive = useRef(true);
  const openRef = useRef(false);
  const aloudRef = useRef(true);
  const conversation = useRef<HTMLDivElement>(null);
  const sendRef = useRef<(text: string) => void>(() => undefined);
  const panel = useRef<HTMLElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);

  function stopSpeech() {
    speechVersion.current += 1;
    speechAbort.current?.abort(); speechAbort.current = null;
    if (audio.current) { audio.current.pause(); audio.current.src = ''; audio.current = null; }
    if (audioUrl.current) { URL.revokeObjectURL(audioUrl.current); audioUrl.current = null; }
    window.speechSynthesis?.cancel();
    if (alive.current) setSpeaking(false);
  }
  function stopListening() {
    const current = recognition.current; recognition.current = null;
    if (current) { current.onend = null; current.onresult = null; current.onerror = null; current.onstart = null; current.abort(); }
    if (alive.current) { setListening(false); setTranscript(''); }
  }
  function closePanel() { openRef.current = false; stopListening(); stopSpeech(); setOpen(false); trigger.current?.focus(); }
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; stopListening(); stopSpeech(); chatAbort.current?.abort(); };
  }, []);
  useEffect(() => {
    if (!open) return;
    let active = true;
    apiFetch<Config>('/api/v1/assistant/config').then(value => { if (active) setConfig(value); })
      .catch(() => { if (active) setNotice('Unable to check assistant availability. You can still try a message.'); });
    panel.current?.focus();
    return () => { active = false; };
  }, [open]);
  useEffect(() => {
    const synth = window.speechSynthesis;
    function update() {
      const voice = synth && chooseIndianVoice(synth.getVoices(), language);
      setVoiceLabel(config?.neural_voice_configured ? (language === 'hi-IN' ? 'Swara · Indian female' : 'Neerja · Indian female')
        : voice ? `${voice.name} · device voice` : 'Device voice · availability varies');
    }
    update(); synth?.addEventListener('voiceschanged', update);
    return () => synth?.removeEventListener('voiceschanged', update);
  }, [config, language]);
  useEffect(() => { conversation.current?.scrollTo({ top: conversation.current.scrollHeight, behavior: 'smooth' }); }, [messages, busy, transcript]);

  async function speak(text: string) {
    stopListening(); stopSpeech();
    const version = speechVersion.current;
    const plain = text.replace(/[*#`]/g, '').slice(0, 1800);
    if (config?.neural_voice_configured) {
      const controller = new AbortController(); speechAbort.current = controller;
      try {
        const response = await apiRequest('/api/v1/assistant/speech', { method: 'POST', body: JSON.stringify({ text: plain, language }), signal: controller.signal });
        if (!response.ok) throw new Error('Neural speech unavailable');
        const blob = await response.blob();
        if (!alive.current || version !== speechVersion.current) return;
        const url = URL.createObjectURL(blob); audioUrl.current = url;
        const player = new Audio(url); audio.current = player;
        const finish = () => { if (version === speechVersion.current) stopSpeech(); };
        player.onended = finish;
        player.onerror = () => { if (version === speechVersion.current) { finish(); setNotice('Audio could not play. Your reply is available in the chat.'); } };
        await player.play();
        if (version === speechVersion.current) setSpeaking(true);
        return;
      } catch {
        if (!alive.current || version !== speechVersion.current) return;
        if (audioUrl.current) { URL.revokeObjectURL(audioUrl.current); audioUrl.current = null; }
        audio.current = null;
        setNotice('Neural voice unavailable. Using a device voice; tap Read reply if playback is blocked.');
      }
    }
    if (!('speechSynthesis' in window)) { setNotice('Speech playback is unavailable in this browser. You can read every reply here.'); return; }
    const utterance = new SpeechSynthesisUtterance(plain);
    const voice = chooseIndianVoice(window.speechSynthesis.getVoices(), language);
    if (voice) utterance.voice = voice;
    utterance.lang = language; utterance.rate = 0.96; utterance.pitch = 1;
    utterance.onstart = () => { if (version === speechVersion.current) setSpeaking(true); };
    utterance.onend = () => { if (version === speechVersion.current) setSpeaking(false); };
    utterance.onerror = event => {
      if (version !== speechVersion.current) return;
      setSpeaking(false);
      if (event.error !== 'canceled' && event.error !== 'interrupted') setNotice('Voice playback is unavailable. Your reply is available in the chat.');
    };
    window.speechSynthesis.speak(utterance);
  }
  async function send(text: string) {
    const message = text.trim();
    if (!message || busyRef.current) return;
    busyRef.current = true; stopListening(); stopSpeech(); setBusy(true); setNotice(''); setInput('');
    const history = messages.slice(1).slice(-12).map(({ role, content }) => ({ role, content: content.slice(0, 4000) }));
    setMessages(previous => [...previous, { role: 'user', content: message }]);
    const controller = new AbortController(); chatAbort.current = controller;
    try {
      const result = await apiFetch<Reply>('/api/v1/assistant/chat', { method: 'POST', body: JSON.stringify({ message, history, language }), signal: controller.signal });
      if (!alive.current) return;
      setMessages(previous => [...previous, { role: 'assistant', content: result.reply, result }]);
      if (result.navigate_url && safeAssistantPath(result.navigate_url)) router.push(result.navigate_url);
      if (aloudRef.current && openRef.current) void speak(result.reply);
    } catch (error) {
      if (!alive.current) return;
      setMessages(previous => [...previous, { role: 'assistant', content: 'I couldn’t receive the task result. Check your connection and application records before retrying.' }]);
      setNotice(error instanceof Error ? error.message : 'Unable to reach the assistant.'); setInput(message);
    } finally { busyRef.current = false; if (alive.current) setBusy(false); }
  }
  sendRef.current = text => { void send(text); };
  function listen() {
    if (recognition.current) { stopListening(); return; }
    if (busyRef.current) return;
    const speechWindow = window as SpeechWindow;
    const RecognitionAPI = speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;
    if (!RecognitionAPI) { setNotice('Voice input is unavailable here. Try Chrome or Edge, or type your instruction.'); return; }
    if (!window.isSecureContext) { setNotice('Microphone input needs HTTPS or localhost. You can type instead.'); return; }
    stopSpeech(); setNotice(''); setTranscript('');
    const current = new RecognitionAPI(); recognition.current = current; setListening(true);
    current.lang = language; current.continuous = false; current.interimResults = true;
    let finalText = ''; let failed = false;
    current.onstart = () => setListening(true);
    current.onresult = event => { finalText = recognitionText(event.results, true); setTranscript(recognitionText(event.results)); };
    current.onerror = event => {
      failed = true; setListening(false);
      const reasons: Record<string, string> = {
        'not-allowed': 'Allow microphone access in your browser, or type your instruction.',
        'audio-capture': 'No microphone was found. Connect one or type your instruction.',
        'no-speech': 'I didn’t hear an instruction. Tap the microphone and try again.',
        network: 'Speech recognition could not connect. Please type your instruction.',
      };
      setNotice(reasons[event.error] || 'Voice input stopped. Please try again or type.');
    };
    current.onend = () => {
      recognition.current = null; setListening(false);
      if (!failed && finalText) sendRef.current(finalText);
      else if (!failed) setNotice('No complete instruction was heard. Please try again.');
    };
    try { current.start(); } catch { recognition.current = null; setListening(false); setNotice('Microphone could not start. Please try again.'); }
  }
  return <>
    <button ref={trigger} onClick={() => { if (open) closePanel(); else { openRef.current = true; setOpen(true); } }} aria-expanded={open} aria-controls="kai-assistant"
      className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-xl hover:bg-emerald-500"><Bot size={20} />Ask KAI</button>
    {open && <section ref={panel} id="kai-assistant" role="dialog" aria-label="KAI career assistant" tabIndex={-1}
      onKeyDown={event => { if (event.key === 'Escape') closePanel(); }}
      className="fixed bottom-20 right-3 z-50 flex max-h-[calc(100dvh-6rem)] w-[calc(100vw-1.5rem)] flex-col overflow-hidden rounded-2xl border border-neutral-700 bg-neutral-900 shadow-2xl sm:right-5 sm:w-[430px]">
      <header className="flex items-center justify-between border-b border-neutral-800 px-4 py-3">
        <div><h2 className="font-semibold">KAI · Your career assistant</h2><p className="text-xs text-neutral-400">AI assistant · {voiceLabel}</p></div>
        <button onClick={closePanel} aria-label="Close assistant" className="rounded p-2 hover:bg-neutral-800"><X size={18} /></button>
      </header>
      <div className="flex flex-wrap items-center gap-3 border-b border-neutral-800 px-4 py-2 text-xs">
        <label>Language <select aria-label="Assistant language" disabled={busy || listening} value={language} onChange={event => { stopSpeech(); setLanguage(event.target.value as AssistantLanguage); }} className="ml-1 rounded bg-neutral-800 p-1">
          <option value="en-IN">English (India)</option><option value="hi-IN">हिन्दी</option></select></label>
        <label className="flex items-center gap-1"><input type="checkbox" checked={readAloud} onChange={event => { aloudRef.current = event.target.checked; setReadAloud(event.target.checked); if (!event.target.checked) stopSpeech(); }} />Read replies aloud</label>
        {speaking && <button onClick={stopSpeech} className="flex items-center gap-1 text-emerald-300"><Square size={12} />Stop voice</button>}
      </div>
      {config && !config.ai_configured && <p className="px-4 pt-3 text-xs text-amber-200">Basic commands available. Add the server’s Gemini key to enable conversations and multi-step tasks.</p>}
      <div ref={conversation} role="log" aria-live="polite" aria-label="Conversation" className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4" style={{ minHeight: '120px' }}>
        {messages.map((message, index) => <article key={index} className={`rounded-xl p-3 text-sm ${message.role === 'user' ? 'ml-6 bg-emerald-950' : 'mr-2 bg-neutral-950'}`}>
          <p className="mb-1 text-xs font-semibold text-neutral-400">{message.role === 'user' ? 'You' : 'KAI'}</p>
          <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
          {message.result && message.result.steps.length > 0 && <ul className="mt-3 space-y-1 border-t border-neutral-800 pt-2 text-xs">
            {message.result.steps.map((step, stepIndex) => <li key={stepIndex} className={step.status === 'completed' ? 'text-emerald-300' : 'text-amber-200'}>{step.status === 'completed' ? '✓' : '!'} {step.summary}</li>)}</ul>}
          {message.result?.links.filter(link => safeAssistantPath(link.url)).map(link => <a key={link.url} href={link.url} className="mt-2 block text-xs text-emerald-300 underline">{link.label} Open →</a>)}
          {message.role === 'assistant' && <button onClick={() => void speak(message.content)} aria-label="Read reply" className="mt-2 inline-flex items-center gap-1 text-xs text-neutral-400 hover:text-white"><Volume2 size={13} />Read reply</button>}
        </article>)}
        {busy && <p role="status" className="text-sm text-emerald-300">Working on your instruction…</p>}
        {listening && <p role="status" className="text-sm text-emerald-300">{transcript || 'Listening… speak your instruction.'}</p>}
      </div>
      <footer className="space-y-3 border-t border-neutral-800 p-4">
        {notice && <p role="alert" className="text-xs text-amber-200">{notice}</p>}
        <div className="flex flex-wrap gap-2">{['Show my profile', 'Search DevOps jobs', 'Show my applications'].map(hint => <button key={hint} disabled={busy || listening} onClick={() => void send(hint)} className="rounded-full border border-neutral-700 px-2 py-1 text-xs text-neutral-300 hover:border-emerald-500 disabled:opacity-50">{hint}</button>)}</div>
        <form onSubmit={event => { event.preventDefault(); void send(input); }} className="flex items-center gap-2">
          <input aria-label="Instruction for KAI" maxLength={2000} value={input} onChange={event => setInput(event.target.value)} disabled={busy || listening} placeholder={language === 'hi-IN' ? 'अपना निर्देश लिखें…' : 'Tell me what to do…'} className="min-w-0 flex-1 rounded-lg border border-neutral-700 bg-neutral-950 px-3 py-3 text-sm focus:border-emerald-500 focus:outline-none" />
          <button type="button" onClick={listen} disabled={busy} aria-label={listening ? 'Cancel listening' : 'Speak to KAI'} aria-pressed={listening} className={`rounded-lg p-3 ${listening ? 'bg-rose-700' : 'bg-neutral-800'} disabled:opacity-50`}>{listening ? <MicOff size={18} /> : <Mic size={18} />}</button>
          <button type="submit" aria-label="Send instruction" disabled={busy || listening || !input.trim()} className="rounded-lg bg-emerald-600 p-3 disabled:opacity-40"><Send size={18} /></button>
        </form>
        <p className="text-[11px] leading-relaxed text-neutral-500">Tasks run while you wait. Prepared records stay in CareerOS until you submit them. Voice input uses your browser’s speech service.</p>
      </footer>
    </section>}
  </>;
}
