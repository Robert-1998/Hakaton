"use client"
import { useState } from "react"
import PromptWizard from "@/components/PromptWizard"
import ImageCard from "@/components/ImageCard"
import type { ImageResult } from "@/lib/api"
import { getImageUrl } from "@/lib/api"

export default function Home() {
    const [images, setImages] = useState<ImageResult[]>([])

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
            <PromptWizard onGenerate={setImages} />

            {/* 🔥 Gallery */}
            {images.length > 0 && (
                <section className="max-w-7xl mx-auto px-6 py-16">
                    <h2 className="text-4xl font-bold text-center mb-16 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                        ✨ Ваши баннеры готовы!
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                        {images.map((img, i) => (
                            <ImageCard
                                key={i}
                                imageUrl={getImageUrl(img.image_path)}
                                title={img.title || "Баннер"}
                                style={img.style || "Photorealistic"}
                            />
                        ))}
                    </div>
                </section>
            )}
        </main>
    )
}
