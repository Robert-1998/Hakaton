"use client"
import { useState } from "react"
import PromptWizard from "@/components/PromptWizard"
import type { ImageResult } from "@/lib/api"
import Gallery from "@/components/Gallery"

export default function Home() {
    const [images, setImages] = useState<ImageResult[]>([
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
        {
            title: "Название",
            image_path: "/images/1.jpg",
        },
    ])

    return (
        <main className="relative flex justify-between gap-[56px] w-full h-full mx-auto p-[40px]">
            {/* <div className="m-[20px] p-[24px] bg-[#6A1BFF] flex justify-between w-full rounded-[32px]"> */}
            <PromptWizard onGenerate={setImages} />
            <Gallery images={images} />
            {/* </div> */}
        </main>
    )
}
