
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  rewrites: async () => {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://127.0.0.1:8001/api/:path*',
        },
      ];
    }

    // Production API routing is handled by vercel.json.
    return [];
  },
};

module.exports = nextConfig;
