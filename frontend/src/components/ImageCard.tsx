"use client"

import { useState } from "react"
import Image from "next/image"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge, X } from "lucide-react"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { cn } from "@/lib/utils" // shadcn utils

interface ImageCardProps {
    imageUrl: string
    title: string
    style: string
}

export default function ImageCard({ imageUrl, title, style }: ImageCardProps) {
    const [isOpen, setIsOpen] = useState(false)

    const handleDownload = () => {
        const link = document.createElement("a")
        link.href = imageUrl
        link.download = `banner-${title.replace(/[^a-z0-9]/giu, "_").toLowerCase()}.png`
        link.rel = "noopener noreferrer"
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        toast.success("✅ Скачано!")
    }

    return (
        <div className="group/card">
            <Card className="relative aspect-video overflow-hidden rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 hover:-translate-y-2">
                <CardContent className="p-0 h-full">
                    <Image
                        src={imageUrl}
                        alt={title}
                        fill
                        className="object-cover transition-all duration-700 hover:scale-105 brightness-100 hover:brightness-110"
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        placeholder="blur"
                        blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/8/AwAkGAigJ9AfK8AAAAASUVORK5CYII="
                        draggable={false}
                    />

                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-black/10 to-transparent opacity-0 group-hover/card:opacity-100 transition-all duration-500 backdrop-blur-sm" />

                    <div className="absolute bottom-6 left-6 right-6 flex gap-3 pointer-events-none opacity-0 group-hover/card:opacity-100 transition-all duration-300">
                        <Dialog open={isOpen} onOpenChange={setIsOpen}>
                            <DialogTrigger asChild>
                                <Button
                                    size="sm"
                                    variant="ghost"
                                    className="flex-1 bg-white/20 backdrop-blur-xl hover:bg-white/40 text-white border-white/40 pointer-events-auto transition-all duration-200"
                                >
                                    👁️ Предпросмотр
                                </Button>
                            </DialogTrigger>
                            <DialogContent
                                className={cn(
                                    "max-w-[1160px] w-[calc(100vw-40px)] max-h-[85vh] p-0 m-0 border-none [&>div]:p-0 [&>button]:hidden",
                                    "lg:w-[calc(100vw-80px)] lg:max-w-[1160px]",
                                )}
                            >
                                {/* 16:9 фиксированное */}
                                <div className="relative w-full pt-[56.25%] aspect-video max-h-[75vh] overflow-hidden">
                                    <Image
                                        src={imageUrl}
                                        alt=""
                                        fill
                                        className="object-cover absolute inset-0"
                                        sizes="1160px"
                                        priority
                                    />
                                    <Button
                                        variant="ghost"
                                        size="lg"
                                        onClick={() => setIsOpen(false)}
                                        className="absolute -top-4 -right-4 w-20 h-20 p-0 bg-black/80 hover:bg-black/95 text-white rounded-3xl backdrop-blur-2xl border-2 border-white/50 shadow-2xl z-[10000] transition-all hover:scale-110"
                                    >
                                        <X className="w-9 h-9" />
                                    </Button>
                                </div>
                            </DialogContent>
                        </Dialog>
                        <Button
                            onClick={handleDownload}
                            size="sm"
                            className="px-6 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white hover:shadow-2xl backdrop-blur-xl border-transparent pointer-events-auto transition-all duration-200 hover:scale-[1.02]"
                        >
                            📥 Скачать
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
