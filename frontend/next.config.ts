import type { NextConfig } from "next"

const nextConfig: NextConfig = {
    images: {
        remotePatterns: [
            { protocol: "http", hostname: "localhost", port: "8000" },
            { protocol: "http", hostname: "backend-web" },
            { protocol: "http", hostname: "127.0.0.1", port: "8000" },
        ],
    },
    async rewrites() {
        return [
            // Browser → Backend (localhost)
            {
                source: "/api/:path*",
                destination: "http://localhost:8000/api/:path*",
            },
            {
                source: "/media/:path*",
                destination: "http://localhost:8000/media/:path*",
            },
            // WS через proxy
            {
                source: "/ws/:path*",
                destination: "http://localhost:8000/ws/:path*",
            },
        ]
    },
}

export default nextConfig
