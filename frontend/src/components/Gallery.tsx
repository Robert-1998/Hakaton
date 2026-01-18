"use client"
import ImageCard from "./ImageCard"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { getImageUrl } from "@/lib/api"
import { Badge } from "./ui/badge"

interface ImageResult {
    title: string
    image_path?: string
    style?: string
}

interface GalleryProps {
    images: ImageResult[]
    onRegenerate?: () => void
}

export default function Gallery({ images, onRegenerate }: GalleryProps) {
    // ✅ Фильтр + safe mapping
    const validImages = images
        .filter((img) => img.image_path) // Только с image_path
        .map((img) => ({
            imageUrl: getImageUrl(img.image_path!), // null-safe!
            title: img.title || "Без названия",
            style: img.style || "Photorealistic",
        }))
        .filter(({ imageUrl }) => imageUrl !== null) // Только с URL

    if (validImages.length === 0) {
        return (
            <div className="text-center py-20">
                <div className="w-32 h-32 mx-auto mb-8 bg-gray-100 rounded-2xl flex items-center justify-center">
                    <span className="text-3xl text-gray-400">🖼</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Изображения не готовы</h3>
                <p className="text-gray-600 mb-8 max-w-md mx-auto">Задача выполняется или произошла ошибка генерации</p>
                {onRegenerate && (
                    <Button onClick={onRegenerate} size="lg">
                        <Plus className="h-5 w-5 mr-2" />
                        Попробовать еще раз
                    </Button>
                )}
            </div>
        )
    }

    return (
        <section className="max-w-7xl mx-auto mt-20">
            <div className="text-center mb-16">
                <h2 className="text-4xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
                    ✨ Ваши баннеры готовы!
                </h2>
                <div className="flex justify-center gap-4 text-sm text-gray-500 mb-8">
                    <Badge variant="secondary">{validImages.length} изображений</Badge>
                    <Badge variant="outline">Готово к скачиванию</Badge>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-8">
                {validImages.map(({ imageUrl, title, style }, i) => (
                    <ImageCard
                        key={i}
                        imageUrl={imageUrl!} // Non-null assertion (уже проверено)
                        title={title}
                        style={style}
                    />
                ))}
            </div>

            <div className="text-center mt-20">
                <Button size="lg" variant="outline" className="text-xl px-12 border-2" onClick={onRegenerate}>
                    🎨 Создать еще баннеры
                </Button>
            </div>
        </section>
    )
}
