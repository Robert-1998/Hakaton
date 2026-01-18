import type { NextConfig } from "next"

const nextConfig: NextConfig = {
    images: {
        remotePatterns: [
            // ✅ Docker + localhost
            { protocol: "http", hostname: "backend-web", port: "" }, // Docker service
            { protocol: "http", hostname: "localhost", port: "8000" },
            { protocol: "http", hostname: "127.0.0.1", port: "8000" },
            { protocol: "http", hostname: "host.docker.internal", port: "8000" }, // Mac Docker
        ],
    },
    async rewrites() {
        return [
            // ✅ Docker приоритет 1
            { source: "/media/:path*", destination: "http://backend-web:8000/media/:path*" },
            { source: "/api/:path*", destination: "http://backend-web:8000/api/:path*" },
            // Fallback localhost (dev без Docker)
            { source: "/media/:path*", destination: "http://localhost:8000/media/:path*" },
            { source: "/api/:path*", destination: "http://localhost:8000/api/:path*" },
        ]
    },
}

export default nextConfig
