"use client";

interface ImagePreviewProps {
    src: string | null;
    alt?: string;
}

export default function ImagePreview({ src, alt = "Preview" }: ImagePreviewProps) {
    if (!src) return null;

    return (
        <div className="border border-gray-200 rounded-lg overflow-hidden shadow-sm bg-gray-50">
            <div className="p-2 bg-white border-b border-gray-100 font-semibold text-gray-700">
                Vista Previa
            </div>
            <div className="relative aspect-[3/4] w-full bg-checkered flex items-center justify-center">
                {/* Usamos img normal por ahora, luego Image de next si configuramos dominios */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                    src={src}
                    alt={alt}
                    className="object-contain max-h-full max-w-full"
                />
            </div>
        </div>
    );
}
