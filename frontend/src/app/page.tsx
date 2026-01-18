"use client"
import PromptWizard from "@/components/PromptWizard"
import Gallery from "@/components/Gallery"
import { useState } from "react"

export default function Home() {
    const [results, setResults] = useState<any[]>([])
    const [loading, setLoading] = useState(false)

    return (
        <main className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
            <div className="container mx-auto px-4 py-12">
                <div className="text-center mb-16">
                    <h1 className="text-5xl font-black bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6">
                        🎨 AI БаннерГен
                    </h1>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                        Опиши идею → Получи готовые баннеры с текстом за 30 секунд
                    </p>
                </div>

                <PromptWizard onGenerate={setResults} loading={loading} />
                {results.length > 0 && <Gallery images={results} />}
            </div>
        </main>
    )
}
