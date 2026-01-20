"use client"
import ImageCard from "./ImageCard"
import { Button } from "@/components/ui/button"
import { getImageUrl } from "@/lib/api"
import { Badge } from "./ui/badge"

interface ImageResult {
    title: string // ✅ Теперь всегда строка!
    image_path?: string
    style?: string
    variant_num?: number
}

interface GalleryProps {
    images: ImageResult[]
    onRegenerate?: () => void
}

export default function Gallery({ images, onRegenerate }: GalleryProps) {
    // 🔥 Теперь работает без нормализации!
    const validImages = images
        .filter((img) => img.image_path) // Только с image_path
        .map((img) => ({
            imageUrl: getImageUrl(img.image_path!),
            title: img.title, // ✅ Строка из API!
            style: img.style || "Photorealistic",
        }))
        .filter(({ imageUrl }) => imageUrl !== null)

    if (validImages.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center w-full mx-[20px]">
                <div className="w-32 h-32 mx-auto mb-8 bg-gray-100 rounded-2xl flex items-center justify-center">
                    <span className="text-3xl text-gray-400">🖼</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Изображения не готовы</h3>
                <p className="text-gray-600 mb-8 max-w-md mx-auto">Задача выполняется или произошла ошибка генерации</p>
                {onRegenerate && (
                    <Button onClick={onRegenerate} size="lg">
                        Попробовать еще раз
                    </Button>
                )}
            </div>
        )
    }

    return (
        <section className="w-full py-[40px] ml-[516px] h-max">
            <div className="mb-[40px]">
                <h2 className="text-[2rem] mb-[20px]">Ваши баннеры готовы!</h2>
                <div className="flex gap-[16px]">
                    <Badge variant="default" className="bg-white text-foreground p-[5px_10px]">
                        {validImages.length} изображений
                    </Badge>
                    <Badge variant="default" className="bg-[#160535] text-white p-[5px_10px]">
                        Готово к скачиванию
                    </Badge>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-3 gap-[24px]">
                {validImages.map(({ imageUrl, title, style }, i) => (
                    <ImageCard
                        key={`${imageUrl}-${i}`} // ✅ Уникальный key
                        imageUrl={imageUrl!}
                        title={title} // ✅ Строка!
                        style={style}
                    />
                ))}
            </div>
        </section>
    )
}
