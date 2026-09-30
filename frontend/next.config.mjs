const staticExport = process.env.STATIC_EXPORT === 'true';
if (staticExport) {
  let api;
  try { api = new URL(process.env.NEXT_PUBLIC_API_URL || ''); } catch { /* Report below. */ }
  if (!api || api.protocol !== 'https:' || api.username || api.password || api.search || api.hash
      || /^(localhost|127\.|0\.|\[::1\])/.test(api.hostname)) {
    throw new Error('Static deployment requires NEXT_PUBLIC_API_URL with a public HTTPS backend URL.');
  }
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(staticExport ? { output: 'export', trailingSlash: true } : {}),
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
