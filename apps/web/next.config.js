/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  },
}

module.exports = nextConfig
