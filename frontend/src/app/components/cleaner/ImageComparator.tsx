"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { MoveHorizontal } from "lucide-react";

interface ImageComparatorProps {
    originalSrc: string;
    cleanedSrc: string;
}

export default function ImageComparator({ originalSrc, cleanedSrc }: ImageComparatorProps) {
    const [isResizing, setIsResizing] = useState(false);
    const [sliderPosition, setSliderPosition] = useState(50); // Percentage
    const containerRef = useRef<HTMLDivElement>(null);

    const handleMouseDown = useCallback(() => setIsResizing(true), []);
    const handleMouseUp = useCallback(() => setIsResizing(false), []);
    const handleMouseMove = useCallback((e: MouseEvent) => {
        if (!isResizing || !containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
        const percentage = (x / rect.width) * 100;

        setSliderPosition(percentage);
    }, [isResizing]);

    useEffect(() => {
        if (isResizing) {
            window.addEventListener("mousemove", handleMouseMove);
            window.addEventListener("mouseup", handleMouseUp);
        }
        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseup", handleMouseUp);
        };
    }, [isResizing, handleMouseMove, handleMouseUp]);

    return (
        <div
            ref={containerRef}
            className="relative w-full h-full select-none overflow-hidden rounded-lg bg-slate-900 border border-slate-800"
        >
            {/* Background Image (Cleaned/Result) */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
                src={cleanedSrc}
                alt="Cleaned"
                className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />

            {/* Foreground Image (Original) - Clipped */}
            <div
                className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none"
                style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
            >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                    src={originalSrc}
                    alt="Original"
                    className="absolute inset-0 w-full h-full object-contain"
                />

                {/* Label Overlay */}
                <div className="absolute top-4 left-4 bg-black/50 backdrop-blur text-white text-xs px-2 py-1 rounded font-mono border border-white/10">
                    ORIGINAL
                </div>
            </div>

            {/* Label Overlay Right */}
            <div className="absolute top-4 right-4 bg-black/50 backdrop-blur text-emerald-400 text-xs px-2 py-1 rounded font-mono border border-emerald-500/20">
                CLEANED
            </div>

            {/* Slider Handle */}
            <div
                className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-10 hover:shadow-[0_0_20px_rgba(255,255,255,0.5)] transition-shadow"
                style={{ left: `${sliderPosition}%` }}
                onMouseDown={handleMouseDown}
            >
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg text-slate-900">
                    <MoveHorizontal className="w-5 h-5" />
                </div>
            </div>
        </div>
    );
}
