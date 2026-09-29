/** Shared API transport for hosted and local deployments. */
export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
export const AUTH_EXPIRED_EVENT = 'careeros:auth-expired';

export function resolveApiUrl(endpoint: string, base = API_BASE_URL): string {
  if (/^[a-z][a-z\d+.-]*:/i.test(endpoint) || endpoint.startsWith('//') || endpoint.includes('\\')) {
    throw new Error('API endpoints must be relative paths');
  }
  const root = base.replace(/\/+$/, '');
  let path = `/${endpoint.replace(/^\/+/, '')}`;
  if (root.endsWith('/api/v1') && (path === '/api/v1' || path.startsWith('/api/v1/'))) {
    path = path.slice('/api/v1'.length);
  }
  return `${root}${path}`;
}

export async function apiRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const url = resolveApiUrl(endpoint);
  const headers = new Headers(options.headers);
  // The browser supplies the multipart boundary when uploading a FormData body.
  if (typeof options.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('careeros_access_token');
    if (token) headers.set('Authorization', `Bearer ${token}`);
  }
  const response = await fetch(url, { ...options, headers, credentials: 'include' });
  if (response.status === 401 && !endpoint.startsWith('/api/v1/auth/') && typeof window !== 'undefined') {
    localStorage.removeItem('careeros_access_token');
    window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
  }
  return response;
}

export async function apiFetch<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await apiRequest(endpoint, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (typeof data.detail === 'string') message = data.detail;
      else if (Array.isArray(data.detail)) message = data.detail.map((item: { msg: string }) => item.msg).join('; ');
    } catch { /* The server may return a non-JSON error. */ }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}
