"use client"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { useState, useTransition, useRef, useEffect, useCallback } from "react"
import { toast } from "sonner"
import type { ImageResult } from "@/lib/api"
import { generateImage } from "@/lib/api"

interface Props {
    onGenerate: (images: ImageResult[]) => void
    loading?: boolean
}

const EXAMPLES = [
    "Современная кофейня в стиле cyberpunk, неоновая вывеска",
    "Минималистичный офис с панорамными окнами",
    "Футуристический спортзал с голограммами",
    "Уютная книжная полка в стиле лофт",
] as const

type Style = "Photorealistic" | "Cyberpunk" | "Anime" | "Watercolor"
type Ratio = "16:9"
type WsStatus = "connecting" | "connected" | "error" | "done"

interface WsMessage {
    status: string
    progress?: number
    result?: any
}

export default function PromptWizard({ onGenerate, loading: externalLoading = false }: Props) {
    const [prompt, setPrompt] = useState("")
    const [style, setStyle] = useState<Style>("Photorealistic")
    const [nImages, setNImages] = useState(1)
    const [isPending, startTransition] = useTransition()
    const [localLoading, setLocalLoading] = useState(false)
    const [taskId, setTaskId] = useState<string | null>(null)
    const [progress, setProgress] = useState(0)
    const [wsStatus, setWsStatus] = useState<WsStatus>("done")

    const inputRef = useRef<HTMLTextAreaElement>(null)
    const wsRef = useRef<WebSocket | null>(null)

    const createWebSocket = useCallback((taskId: string) => {
        const wsUrl = `${(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
            /^http/,
            "ws",
        )}/ws/${taskId}`

        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
            console.log("✅ WebSocket connected:", taskId)
            setWsStatus("connected")
        }

        ws.onmessage = (event) => {
            const data: WsMessage = JSON.parse(event.data)
            console.log("📡 WS:", data.status, data)

            if (data.progress !== undefined) {
                setProgress(Math.round(data.progress))
            }

            if (data.status === "SUCCESS") {
                console.log("🎨 SUCCESS result:", data.result)
                setWsStatus("done")
                setProgress(100)
            } else if (data.status === "FAILURE") {
                setWsStatus("error")
            }
        }

        ws.onerror = () => setWsStatus("error")
        ws.onclose = () => {
            console.log("WebSocket closed")
            setWsStatus("done")
        }

        return () => {
            ws.close()
            wsRef.current = null
        }
    }, [])

    useEffect(() => {
        if (!taskId || wsStatus === "done") return
        return createWebSocket(taskId)
    }, [taskId, wsStatus, createWebSocket])

    const handleGenerate = useCallback(() => {
        if (!prompt.trim()) {
            toast.error("Введите описание баннера!")
            inputRef.current?.focus()
            return
        }

        startTransition(async () => {
            try {
                const promiseId = toast.loading("📡 Отправляем задачу Celery...")
                const result = await generateImage({
                    prompt: prompt.trim(),
                    style,
                    n_images: nImages,
                })

                console.log("🎨 PromptWizard result:", result)
                toast.success(`✨ ${Array.isArray(result) ? result.length : 1} баннеров готово!`, {
                    id: promiseId,
                })
                onGenerate(Array.isArray(result) ? result : [result])

                // Reset state
                setTaskId(null)
                setProgress(0)
                setWsStatus("done")
            } catch (error: any) {
                toast.error(error.message || "Ошибка генерации")
            }
        })
    }, [prompt, style, nImages, onGenerate])

    const handleCancel = useCallback(() => {
        setLocalLoading(false) // ✅ Мгновенный сброс
        setTaskId(null)
        setProgress(0)
        setWsStatus("done")
        wsRef.current?.close()
        toast.info("⏹️ Остановлено")
    }, [])

    const isLoading = externalLoading || localLoading || isPending || wsStatus !== "done"

    return (
        <>
            {/* Main Form */}
            <div className="max-w-[460px] w-full h-max bg-white p-[40px] flex flex-col gap-[40px] rounded-[32px] fixed top-[40px]">
                <h2 className="text-[2rem]">AI media generator</h2>
                <div className="flex items-start gap-[20px]">
                    <div className="flex-1 w-full">
                        <label className="text-sm font-semibold text-gray-900 mb-[10px] block">Стиль</label>
                        <Select value={style} onValueChange={(value: Style) => setStyle(value)} disabled={isLoading}>
                            <SelectTrigger className="w-full h-[40px] rounded-[8px]">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="Photorealistic">📸 Фотореализм</SelectItem>
                                <SelectItem value="Cyberpunk">🌃 Киберпанк</SelectItem>
                                <SelectItem value="Anime">🎌 Аниме</SelectItem>
                                <SelectItem value="Watercolor">🖌 Акварель</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="flex-1 w-full">
                        <label className="text-sm font-semibold text-gray-900 mb-[10px] block">Вариантов</label>
                        <Slider
                            value={[nImages]}
                            onValueChange={(v) => setNImages(v[0])}
                            min={1}
                            max={4}
                            step={1}
                            className="w-full h-[36px]"
                            disabled={isLoading}
                        />
                        <Badge variant="secondary" className="w-full justify-center p-0">
                            {nImages} {nImages > 1 ? "изображений" : "изображение"}
                        </Badge>
                    </div>
                </div>

                <div className="flex flex-col gap-[20px]">
                    <label className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        Описание баннера
                    </label>
                    <Textarea
                        ref={inputRef as React.RefObject<HTMLTextAreaElement>}
                        placeholder="Современная кофейня в стиле cyberpunk с неоновой вывеской..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="rounded-[16px] h-[200px] resize-vertical"
                        disabled={isLoading}
                    />

                    <div className="flex flex-col sm:flex-row gap-4">
                        <Button
                            onClick={handleGenerate}
                            disabled={isLoading || !prompt.trim()}
                            className="flex-1 h-[56px] text-[1rem] rounded-[16px] font-semibold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600"
                        >
                            {isLoading ? (
                                <>Генерируем...</>
                            ) : (
                                <>Создать {nImages > 1 ? `${nImages} вариантов` : "баннер"}</>
                            )}
                        </Button>

                        {isLoading && (
                            <Button
                                onClick={handleCancel}
                                variant="outline"
                                className="flex-1 h-[56px] text-[1rem] rounded-[16px] font-semibold shrink-0"
                            >
                                Прервать
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        </>
    )
}
