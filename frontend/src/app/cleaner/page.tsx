"use client";

import { useState } from "react";
import ImageComparator from "@/app/components/cleaner/ImageComparator";
import CleanerToolbar from "@/app/components/cleaner/CleanerToolbar";

export default function CleanerPage() {
    // Mock Data for UI Demonstration
    const [original] = useState("https://placehold.co/800x1200/222/FFF/png?text=Original+Scan");
    const [cleaned] = useState("https://placehold.co/800x1200/222/4ade80/png?text=Cleaned+Result");

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)]">
            {/* Header / Context */}
            <div className="mb-4 flex justify-between items-end">
                <div>
                    <h1 className="text-2xl font-bold text-white">Magic Cleaner Workspace</h1>
                    <p className="text-slate-400 text-sm">Reviewing: <span className="text-indigo-400 font-mono">Chapter_145_Page_03.jpg</span></p>
                </div>
                <div className="flex gap-2 text-xs">
                    <span className="px-2 py-1 bg-slate-800 rounded text-slate-400">Resolution: 1400x2100</span>
                    <span className="px-2 py-1 bg-slate-800 rounded text-slate-400">Inpainting: Telea (Fast)</span>
                </div>
            </div>

            {/* Main Workspace Canvas */}
            <div className="flex-1 relative bg-slate-950/50 rounded-xl overflow-hidden border border-slate-800 border-dashed flex items-center justify-center p-4">
                {/* Container for the comparator constrained to viewport to avoid scroll */}
                <div className="relative h-full aspect-[2/3] max-w-full shadow-2xl">
                    <ImageComparator
                        originalSrc={original}
                        cleanedSrc={cleaned}
                    />
                </div>
            </div>

            {/* Toolbar */}
            <CleanerToolbar />
        </div>
    );
}
