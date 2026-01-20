"use client"
import { Progress } from "@/components/ui/progress"

interface Props {
    status: "pending" | "generating" | "uploading" | "complete"
    progress?: number
}

export default function ProgressSpinner({ status, progress = 0 }: Props) {
    const steps = {
        pending: { label: "Получаем идею...", value: 25 },
        generating: { label: "Генерируем изображения...", value: 75 },
        uploading: { label: "Загружаем результат...", value: 95 },
        complete: { label: "Готово!", value: 100 },
    }

    const step = steps[status]

    return (
        <div className="max-w-md mx-auto bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-12 border border-white/50">
            <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{step.label}</h3>
                <p className="text-gray-500">Это займет около 30 секунд</p>
            </div>

            <Progress
                value={progress || step.value}
                className="w-full h-3 [&>div]:!bg-gradient-to-r [&>div]:from-indigo-500 [&>div]:to-purple-600"
            />
            <div className="flex justify-between text-sm text-gray-500 mt-2">
                <span>0%</span>
                <span>{Math.round(progress || step.value)}%</span>
                <span>100%</span>
            </div>
        </div>
    )
}
