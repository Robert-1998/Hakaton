const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface GeneratePayload {
    prompt: string
    style: string
    aspect_ratio: string
    n_images: number
}

export interface ImageResult {
    title: string
    image_path?: string
    style?: string
    variant_num?: number
}

// 🔥 ПРАВИЛЬНЫЙ extractVariants()
function extractVariants(data: any): ImageResult[] {
    console.log("🔍 extractVariants input:", data) // 🔥 DEBUG!

    // Пробуем разные пути Celery
    const paths = [data.result?.result?.variants, data.result?.variants, data.result, data.variants, data]

    for (const candidate of paths) {
        // ✅ candidate вместо path
        if (Array.isArray(candidate)) return candidate
        if (candidate?.variants?.length) return candidate.variants
    }

    // Если последний объект → [object]
    const lastCandidate = paths[paths.length - 1]
    if (lastCandidate && typeof lastCandidate === "object") {
        return [lastCandidate as ImageResult]
    }

    console.error("❌ Нет variants:", data)
    return []
}

export async function generateImage(payload: GeneratePayload): Promise<ImageResult[]> {
    const res = await fetch(`${API_URL}/api/v1/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })

    if (!res.ok) throw new Error(`API Error: ${res.status}`)
    const { task_id } = await res.json()

    console.log("🚀 Task started:", task_id)

    try {
        return await waitForWebSocket(task_id)
    } catch (wsError) {
        console.warn("WebSocket failed → polling:", wsError)
        return pollTask(task_id)
    }
}

async function waitForWebSocket(taskId: string): Promise<ImageResult[]> {
    return new Promise((resolve, reject) => {
        const wsUrl = `${API_URL.replace("http", "ws")}/ws/${taskId}`
        const ws = new WebSocket(wsUrl)

        let timeoutId: NodeJS.Timeout

        ws.onopen = () => {
            console.log("✅ WS connected:", taskId)
            timeoutId = setTimeout(() => {
                ws.close()
                reject(new Error("WS timeout"))
            }, 60000) // 1 мин
        }

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            console.log("📡 WS:", data.status, taskId)

            clearTimeout(timeoutId)

            if (data.status === "SUCCESS") {
                ws.close()
                resolve(extractVariants(data)) // 🔥 Фикс!
            } else if (data.status === "FAILURE") {
                ws.close()
                reject(new Error(data.result?.error || "Failed"))
            }
        }

        ws.onerror = () => {
            clearTimeout(timeoutId)
            ws.close()
            reject(new Error("WS error"))
        }

        ws.onclose = () => clearTimeout(timeoutId)
    })
}

async function pollTask(taskId: string): Promise<ImageResult[]> {
    let delay = 500 // 🔥 Быстро!
    const maxAttempts = 120 // 1 мин

    for (let i = 0; i < maxAttempts; i++) {
        const res = await fetch(`${API_URL}/api/v1/status/${taskId}`)
        const data = await res.json()

        console.log(`🔄 Poll ${i + 1}:`, data.status)

        if (data.status === "SUCCESS") {
            console.log("✅ SUCCESS data:", data)
            return extractVariants(data) // 🔥 Фикс!
        }
        if (data.status === "FAILURE") {
            throw new Error(data.result?.error || "Failed")
        }

        await new Promise((r) => setTimeout(r, delay))
        delay = Math.min(delay * 1.1, 2000)
    }
    throw new Error("⏰ Timeout 1min")
}

export function getImageUrl(imagePath?: string | null): string | null {
    if (!imagePath) return null
    const filename = imagePath.split("/").pop()!
    return `/media/${filename}` // Public folder!
}
