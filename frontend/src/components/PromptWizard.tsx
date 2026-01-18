"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useState, useTransition, useRef, useEffect, useCallback } from "react"
import { Wand2, ImagePlus, Sparkles, StopCircle } from "lucide-react"
import { toast, Toaster } from "sonner"
import type { ImageResult } from "@/lib/api"
import { generateImage } from "@/lib/api"

interface Props {
    onGenerate: (images: ImageResult[]) => void
    loading?: boolean
}

export default function PromptWizard({ onGenerate, loading: externalLoading = false }: Props) {
    const [prompt, setPrompt] = useState("")
    const [style, setStyle] = useState("Photorealistic")
    const [ratio, setRatio] = useState("1:1")
    const [nImages, setNImages] = useState(2)
    const [isPending, startTransition] = useTransition()
    const [taskId, setTaskId] = useState<string | null>(null)
    const [progress, setProgress] = useState(0)
    const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "error" | "done">("done")
    const inputRef = useRef<HTMLInputElement>(null)
    const wsRef = useRef<WebSocket | null>(null)

    const examples = [
        "Современная кофейня в стиле cyberpunk, неоновая вывеска",
        "Минималистичный офис с панорамными окнами",
        "Футуристический спортзал с голограммами",
        "Уютная книжная полка в стиле лофт",
    ] as const

    const setExample = useCallback((example: string) => {
        setPrompt(example)
        toast.message("Пример загружен!")
    }, [])

    useEffect(() => {
        if (!taskId || wsStatus === "done") return

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
            const data = JSON.parse(event.data) as { status: string; progress?: number; result?: any }
            console.log("📡 WS:", data.status, data)

            if (data.progress !== undefined) {
                setProgress(Math.round(data.progress))
            }

            if (data.status === "SUCCESS") {
                console.log("🎨 SUCCESS result:", data.result) // 🔥 DEBUG!
                setWsStatus("done")
                setProgress(100)
            } else if (data.status === "FAILURE") {
                setWsStatus("error")
            }
        }

        ws.onerror = (error) => {
            console.error("WebSocket error:", error)
            setWsStatus("error")
        }

        ws.onclose = () => {
            console.log("WebSocket closed")
            setWsStatus("done")
        }

        return () => {
            ws.close()
            wsRef.current = null
        }
    }, [taskId, wsStatus])

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
                    aspect_ratio: ratio,
                    n_images: nImages,
                })

                console.log("🎨 PromptWizard result:", result) // 🔥 DEBUG!

                toast.success(`✨ ${Array.isArray(result) ? result.length : 1} баннеров готово!`, {
                    id: promiseId,
                })
                onGenerate(Array.isArray(result) ? result : [result]) // 🔥 CALLBACK!

                setTaskId(null)
                setProgress(0)
                setWsStatus("done")
            } catch (error: any) {
                toast.error(error.message || "Ошибка генерации")
            }
        })
    }, [prompt, style, ratio, nImages, onGenerate])

    const handleCancel = useCallback(() => {
        setTaskId(null)
        setProgress(0)
        setWsStatus("done")
        wsRef.current?.close()
        toast.info("⏹️ Остановлено")
    }, [])

    const isLoading = externalLoading || isPending || wsStatus !== "done"

    return (
        <>
            <Toaster position="top-center" richColors />
            <div className="max-w-6xl mx-auto p-4 md:p-8">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
                    {examples.map((example, i) => (
                        <Card
                            key={i}
                            className="p-4 h-24 cursor-pointer hover:shadow-lg transition-all group hover:bg-indigo-50 border-2 border-transparent hover:border-indigo-200"
                            onClick={() => setExample(example)}
                        >
                            <CardContent className="p-0 h-full flex items-center group-hover:text-indigo-600">
                                <p className="text-sm line-clamp-3 font-medium leading-relaxed">{example}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <div className="max-w-4xl mx-auto bg-gradient-to-br from-white/90 to-indigo-50/70 backdrop-blur-xl rounded-3xl shadow-2xl p-8 md:p-12 border border-white/50">
                    <div className="grid md:grid-cols-3 gap-6 lg:gap-8 mb-10 md:mb-12">
                        <div className="md:col-span-2 space-y-3">
                            <label className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                <Wand2 className="h-5 w-5 text-indigo-600" />
                                Описание баннера
                            </label>
                            <Input
                                ref={inputRef}
                                placeholder="Современная кофейня в стиле cyberpunk с неоновой вывеской..."
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                className="h-20 text-xl p-6 placeholder-gray-400 border-2 border-gray-200 focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-indigo-200 resize-none font-medium"
                                disabled={isLoading}
                            />
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="text-sm font-semibold text-gray-900 mb-2 block">🎨 Стиль</label>
                                <Select value={style} onValueChange={setStyle} disabled={isLoading}>
                                    <SelectTrigger className="w-full h-12">
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

                            <div>
                                <label className="text-sm font-semibold text-gray-900 mb-2 block">📐 Формат</label>
                                <Select value={ratio} onValueChange={setRatio} disabled={isLoading}>
                                    <SelectTrigger className="w-full h-12">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="1:1">Квадрат 1:1</SelectItem>
                                        <SelectItem value="16:9">Широкий 16:9</SelectItem>
                                        <SelectItem value="4:3">Постер 4:3</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div>
                                <label className="text-sm font-semibold text-gray-900 mb-2 block">🔢 Вариантов</label>
                                <Slider
                                    value={[nImages]}
                                    onValueChange={(v) => setNImages(v[0])}
                                    min={1}
                                    max={4}
                                    step={1}
                                    className="w-full"
                                    disabled={isLoading}
                                />
                                <Badge variant="secondary" className="mt-2 w-full justify-center">
                                    {nImages} {nImages > 1 ? "изображений" : "изображение"}
                                </Badge>
                            </div>
                        </div>
                    </div>

                    {isLoading && (
                        <div className="mb-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border">
                            <div className="flex justify-between items-center mb-3">
                                <span className="font-semibold text-lg">Генерация: {Math.round(progress)}%</span>
                                {wsStatus === "connected" && (
                                    <Badge variant="outline" className="flex items-center gap-1 text-xs">
                                        <Sparkles className="h-3 w-3 animate-pulse" />
                                        Live
                                    </Badge>
                                )}
                            </div>
                            <Progress
                                value={progress}
                                className="w-full h-4 [&>div]:!bg-gradient-to-r [&>div]:from-indigo-500 [&>div]:to-purple-600"
                            />
                            {taskId && (
                                <div className="text-xs text-gray-500 font-mono mt-2 truncate bg-gray-100 px-2 py-1 rounded">
                                    {taskId.slice(0, 8)}...
                                </div>
                            )}
                        </div>
                    )}

                    <div className="flex flex-col sm:flex-row gap-4">
                        <Button
                            onClick={handleGenerate}
                            disabled={isLoading || !prompt.trim()}
                            className="flex-1 h-16 md:h-20 text-lg font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 shadow-2xl shadow-indigo-500/25 text-white hover:shadow-indigo-600/30 transition-all duration-200"
                        >
                            {isLoading ? (
                                <>
                                    <Sparkles className="h-5 w-5 mr-2 animate-spin" />
                                    Генерируем...
                                </>
                            ) : (
                                <>
                                    <ImagePlus className="h-5 w-5 mr-2" />
                                    Создать {nImages > 1 ? `${nImages} вариантов` : "баннер"}
                                </>
                            )}
                        </Button>

                        {isLoading && (
                            <Button
                                onClick={handleCancel}
                                variant="outline"
                                className="h-16 md:h-20 px-8 border-2 border-gray-200 hover:border-gray-300 hover:bg-gray-50 shrink-0"
                            >
                                <StopCircle className="h-5 w-5 mr-2" />
                                Прервать
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        </>
    )
}
