const isProduction = process.env.NODE_ENV === 'production' || process.env.GITHUB_ACTIONS || false;

let repo = '';
if (process.env.GITHUB_REPOSITORY) {
  repo = process.env.GITHUB_REPOSITORY.replace(/.*?\//, '');
} else {
  repo = 'CareerOS_Infinity';
}

const basePath = process.env.NEXT_PUBLIC_BASE_PATH !== undefined 
  ? process.env.NEXT_PUBLIC_BASE_PATH 
  : (isProduction ? `/${repo}` : '');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: isProduction && basePath ? basePath : undefined,
  assetPrefix: isProduction && basePath ? basePath : undefined,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
