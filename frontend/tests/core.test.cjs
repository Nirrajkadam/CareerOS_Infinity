const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const ts = require('typescript');

function loadTypeScript(relativePath) {
  const filename = path.resolve(__dirname, relativePath);
  const source = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  const mod = new Module(filename, module);
  mod._compile(source, filename);
  return mod.exports;
}
const { summarizeApplications, recentApplications, isVerifiedSubmission } = loadTypeScript('../src/lib/dashboard.ts');
const { resolveApiUrl, apiRequest, apiFetch } = loadTypeScript('../src/lib/apiClient.ts');
const now = Date.parse('2026-09-27T12:00:00Z');

test('empty feed has zero counts and no invented ATS score', () => {
  assert.deepEqual(summarizeApplications([], now), { activeApplications: 0, avgAtsMatch: null, appliesThisWeek: 0 });
});
test('ATS averages retain zero and ignore missing, invalid and unrelated scores', () => {
  assert.equal(summarizeApplications([
    { ats_score: 0 }, { ats_score: 80 }, { ats_score: null, job_fit_score: 95 },
    { ats_score: '85' }, { ats_score: NaN }, { ats_score: 101 },
  ], now).avgAtsMatch, 40);
});
test('weekly submissions exclude drafts, future dates and old submissions', () => {
  const summary = summarizeApplications([
    { status: 'DRAFT', created_at: '2026-09-26T12:00:00Z', applied_at: '2026-09-26T12:00:00Z' },
    { status: 'SUBMITTED', applied_at: '2026-09-21T12:00:00Z' },
    { status: 'REJECTED', submitted_at: '2026-09-22T12:00:00Z' },
    { status: 'SUBMITTED', submitted_at: '2026-09-01T12:00:00Z' },
    { status: 'SUBMITTED', submitted_at: '2026-10-01T12:00:00Z' },
    { status: 'SUBMITTED', submitted_at: 'bad date' },
  ], now);
  assert.equal(summary.appliesThisWeek, 2);
  assert.equal(summary.activeApplications, 5);
});
test('submitted status alone does not claim verified evidence', () => {
  assert.equal(isVerifiedSubmission('SUBMITTED'), false);
  assert.equal(isVerifiedSubmission('SUBMITTED_VERIFIED'), true);
});
test('recent feed is sorted by recorded time without mutating input', () => {
  const input = [{ id: 'old', created_at: '2026-01-01' }, { id: 'new', created_at: '2026-09-27' }];
  assert.equal(recentApplications(input)[0].id, 'new');
  assert.equal(input[0].id, 'old');
});
test('API origin and prefixed configuration both produce one API prefix', () => {
  assert.equal(resolveApiUrl('/api/v1/resumes', 'https://api.example.com/'), 'https://api.example.com/api/v1/resumes');
  assert.equal(resolveApiUrl('/api/v1/resumes', 'https://api.example.com/api/v1/'), 'https://api.example.com/api/v1/resumes');
  assert.equal(resolveApiUrl('/resumes', '/api/v1'), '/api/v1/resumes');
});
test('absolute URLs cannot receive the API bearer token', () => {
  for (const endpoint of ['https://other.example/data', '//other.example/data', '\\other.example']) {
    assert.throws(() => resolveApiUrl(endpoint));
  }
});
test('API transport handles Headers, auth, multipart, empty responses and expiry', async () => {
  const originalFetch = global.fetch;
  const originalWindow = global.window;
  const originalStorage = global.localStorage;
  let token = 'test-token';
  let expired = false;
  let received;
  global.window = { dispatchEvent: () => { expired = true; } };
  global.localStorage = { getItem: () => token, removeItem: () => { token = null; } };
  global.fetch = async (url, options) => { received = { url, options }; return new Response(null, { status: 204 }); };
  try {
    const body = new FormData();
    body.append('file', new Blob(['resume']), 'resume.txt');
    await apiRequest('/api/v1/resumes/upload', { method: 'POST', body, headers: new Headers({ 'X-Test': 'yes' }) });
    assert.equal(received.options.headers.get('Content-Type'), null);
    assert.equal(received.options.headers.get('Authorization'), 'Bearer test-token');
    assert.equal(received.options.headers.get('X-Test'), 'yes');
    assert.equal(received.options.credentials, 'include');
    assert.equal(await apiFetch('/api/v1/test'), undefined);
    global.fetch = async () => new Response('{"detail":"expired"}', { status: 401 });
    await assert.rejects(apiFetch('/api/v1/resumes'), /expired/);
    assert.equal(expired, true);
    assert.equal(token, null);
  } finally {
    global.fetch = originalFetch;
    global.window = originalWindow;
    global.localStorage = originalStorage;
  }
});
