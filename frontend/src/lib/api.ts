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
    variant_num?: number // ✅ Для множественных вариантов
}

// ==========================================================
// WebSocket версия (основная) + Fallback на polling
// ==========================================================

export async function generateImage(payload: GeneratePayload): Promise<ImageResult[]> {
    const res = await fetch(`${API_URL}/api/v1/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })

    if (!res.ok) throw new Error(`API Error: ${res.status}`)
    const { task_id } = await res.json()

    console.log("🚀 Task started:", task_id)

    // ✅ WebSocket + fallback
    try {
        return await waitForWebSocket(task_id)
    } catch (wsError) {
        console.warn("WebSocket failed, fallback to polling:", wsError)
        return pollTask(task_id)
    }
}

// WebSocket ожидание (профессионально!)
async function waitForWebSocket(taskId: string): Promise<ImageResult[]> {
    return new Promise((resolve, reject) => {
        const wsUrl = `${API_URL.replace("http", "ws").replace("https", "wss")}/ws/${taskId}`
        const ws = new WebSocket(wsUrl)

        let timeoutId: NodeJS.Timeout

        ws.onopen = () => {
            console.log("✅ WebSocket connected:", taskId)
            // Timeout 5 мин на всякий случай
            timeoutId = setTimeout(() => {
                ws.close()
                reject(new Error("WebSocket timeout 5min"))
            }, 300000)
        }

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            console.log("📡 WS update:", data.status, taskId)

            clearTimeout(timeoutId)

            if (data.status === "SUCCESS") {
                ws.close()
                const results = (data.result.variants || data.result) as ImageResult[]
                resolve(filterValidImages(results)) // Фильтруем error_
            } else if (data.status === "FAILURE") {
                ws.close()
                reject(new Error(data.result?.error || data.error || "Task failed"))
            }
        }

        ws.onerror = (error) => {
            clearTimeout(timeoutId)
            ws.close()
            reject(new Error(`WebSocket error: ${error}`))
        }

        ws.onclose = (event) => {
            clearTimeout(timeoutId)
            if (event.code !== 1000) {
                // Нормальное закрытие = 1000
                console.warn("WS closed unexpectedly:", event.code, event.reason)
            }
        }
    })
}

// ✅ Улучшенный polling (fallback)
async function pollTask(taskId: string): Promise<ImageResult[]> {
    let delay = 2000
    const maxAttempts = 240 // 8 мин

    for (let i = 0; i < maxAttempts; i++) {
        const res = await fetch(`${API_URL}/api/v1/status/${taskId}`)
        const data = await res.json()

        console.log(`🔄 Poll ${i + 1}/${maxAttempts}: ${data.status}`)

        if (data.status === "SUCCESS") {
            return filterValidImages(data.result.variants || data.result)
        }
        if (data.status === "FAILURE") {
            throw new Error(data.result?.error || data.error || "Task failed")
        }

        await new Promise((r) => setTimeout(r, delay))
        delay = Math.min(delay * 1.2, 10000) // Backoff
    }
    throw new Error("⏰ Timeout 8min — backend слишком медленный")
}

// ✅ Фильтр валидных изображений (убираем error_)
function filterValidImages(results: ImageResult[]): ImageResult[] {
    return results.filter((img) => img.image_path && !img.image_path.includes("error_"))
}

// ✅ Null-safe URL (без изменений)
export function getImageUrl(imagePath?: string | null): string | null {
    if (!imagePath || imagePath === "undefined" || imagePath === "" || imagePath.includes("error_")) return null

    const filename = imagePath.split("/").pop() || "placeholder.png"
    return `/media/${filename}`
}

// ✅ Бонус: Отмена задачи (если добавите DELETE /cancel/{task_id})
export async function cancelTask(taskId: string): Promise<void> {
    await fetch(`${API_URL}/api/v1/cancel/${taskId}`, { method: "DELETE" })
}
