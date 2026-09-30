export type AssistantLanguage = 'en-IN' | 'hi-IN';
export type VoiceOption = { name: string; lang: string };
export function chooseIndianVoice<T extends VoiceOption>(voices: T[], language: AssistantLanguage): T | undefined {
  const local = voices.filter(voice => voice.lang.toLowerCase().replace('_', '-') === language.toLowerCase());
  return local.find(voice => /neerja|swara|heera|kalpana|female/i.test(voice.name))
    || local[0] || voices.find(voice => voice.lang.startsWith(language.slice(0, 2)));
}
export function safeAssistantPath(path: string): boolean {
  return /^\/(?:jobs|resume|applications|profile)?$/.test(path)
    || /^\/applications\/detail\/\?id=[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(path);
}
export function recognitionText(results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }>, finalOnly = false): string {
  return Array.from(results).filter(result => !finalOnly || result.isFinal).map(result => result[0].transcript).join(' ').trim();
}
