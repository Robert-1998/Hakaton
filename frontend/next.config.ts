import type { NextConfig } from "next"

const nextConfig: NextConfig = {
    images: {
        remotePatterns: [
            // 🔥 Точное разрешение /media/ только!
            {
                protocol: "http",
                hostname: "localhost",
                port: "8000",
                pathname: "/media/**",
            },
            {
                protocol: "http",
                hostname: "127.0.0.1",
                port: "8000",
                pathname: "/media/**",
            },
            {
                protocol: "http",
                hostname: "backend-web",
                port: "8000",
                pathname: "/media/**",
            },
        ],
    },
    async rewrites() {
        return [
            { source: "/api/:path*", destination: "http://localhost:8000/api/:path*" },
            { source: "/ws/:path*", destination: "http://localhost:8000/ws/:path*" },
        ]
    },
}

export default nextConfig
