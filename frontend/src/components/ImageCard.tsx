"use client"
import Image from "next/image"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, RefreshCw } from "lucide-react"
import { toast } from "sonner"
import { Badge } from "./ui/badge"

interface ImageCardProps {
    imageUrl: string | null
    title: string
    style: string
}

export default function ImageCard({ imageUrl, title, style }: ImageCardProps) {
    // ✅ Если нет изображения — placeholder
    if (!imageUrl) {
        return (
            <Card className="animate-pulse border-dashed border-2 border-gray-200">
                <CardContent className="p-8 flex flex-col items-center justify-center h-80 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-gray-200 to-gray-300 rounded-2xl flex items-center justify-center mb-4">
                        <RefreshCw className="h-8 w-8 text-gray-500 animate-spin" />
                    </div>
                    <p className="text-gray-500 text-sm">Изображение недоступно</p>
                    <p className="text-xs text-gray-400 mt-1">{style}</p>
                </CardContent>
            </Card>
        )
    }

    const download = () => {
        const link = document.createElement("a")
        link.href = imageUrl
        link.download = `banner-${title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        toast.success("Скачано в Загрузки!")
    }

    return (
        <Card className="group hover:shadow-2xl transition-all duration-500 overflow-hidden border-0 bg-white/80 backdrop-blur-sm hover:bg-white">
            <CardContent className="p-0">
                <div className="relative h-80 w-full">
                    <Image
                        src={imageUrl}
                        alt={title}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-700 brightness-100 group-hover:brightness-105"
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        placeholder="blur"
                        blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/8/AwAkGAigJ9AfK8AAAAASUVORK5CYII="
                        onError={(e) => {
                            console.error("Image load failed:", imageUrl)
                            e.currentTarget.style.display = "none"
                        }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>

                <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <Badge
                            variant="secondary"
                            className="px-3 py-1 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800"
                        >
                            {style}
                        </Badge>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={download}
                            className="opacity-0 group-hover:opacity-100 transition-all p-2 h-auto w-auto"
                        >
                            <Download className="h-4 w-4" />
                        </Button>
                    </div>
                    <h3 className="font-bold text-lg leading-tight line-clamp-2 group-hover:text-indigo-900 transition-colors">
                        {title}
                    </h3>
                </div>
            </CardContent>
        </Card>
    )
}
