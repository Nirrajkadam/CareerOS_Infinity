const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const ts = require('typescript');
const filename = path.resolve(__dirname, '../src/lib/assistant.ts');
const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const mod = new Module(filename, module); mod._compile(code, filename);
const { chooseIndianVoice, recognitionText, safeAssistantPath } = mod.exports;

test('Indian voices take priority over US/UK voices and female Indian names are preferred', () => {
  const voices = [{ name: 'US Female', lang: 'en-US' }, { name: 'Prabhat', lang: 'en-IN' }, { name: 'Neerja', lang: 'en-IN' }, { name: 'Swara', lang: 'hi-IN' }];
  assert.equal(chooseIndianVoice(voices, 'en-IN').name, 'Neerja');
  assert.equal(chooseIndianVoice(voices, 'hi-IN').name, 'Swara');
  assert.equal(chooseIndianVoice([], 'en-IN'), undefined);
});
test('recognition collects all final segments without sending interim text', () => {
  const results = [{ isFinal: true, 0: { transcript: 'Find DevOps' } }, { isFinal: true, 0: { transcript: 'jobs in Pune' } }, { isFinal: false, 0: { transcript: 'and maybe' } }];
  assert.equal(recognitionText(results, true), 'Find DevOps jobs in Pune');
  assert.equal(recognitionText(results), 'Find DevOps jobs in Pune and maybe');
});
test('assistant links cannot navigate to external or unsupported destinations', () => {
  for (const unsafe of ['https://evil.test', '//evil.test', '/settings/credentials', '/jobs?next=https://evil.test', '/applications/../profile', 'javascript:alert(1)']) assert.equal(safeAssistantPath(unsafe), false);
  for (const safe of ['/', '/resume', '/jobs', '/applications/detail/?id=01234567-1234-1234-1234-012345678901']) assert.equal(safeAssistantPath(safe), true);
});
