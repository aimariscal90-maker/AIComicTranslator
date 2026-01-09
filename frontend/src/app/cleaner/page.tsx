"use client";

import { useState } from "react";
import ImageComparator from "@/app/components/cleaner/ImageComparator";
import CleanerToolbar from "@/app/components/cleaner/CleanerToolbar";
import EditorModal from "@/app/components/editor/EditorModal";
import CanvasEditor from "@/app/components/editor/CanvasEditor";
import { Edit3 } from "lucide-react";

export default function CleanerPage() {
    // Mock Data for UI Demonstration
    const [original] = useState("https://placehold.co/800x1200/222/FFF/png?text=Original+Scan");
    const [cleaned] = useState("https://placehold.co/800x1200/222/4ade80/png?text=Cleaned+Result");

    // Day 07 Integration
    const [isEditorOpen, setIsEditorOpen] = useState(false);

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] relative">

            {/* Header / Context */}
            <div className="mb-4 flex justify-between items-end">
                <div>
                    <h1 className="text-2xl font-bold text-white">Magic Cleaner Workspace</h1>
                    <p className="text-slate-400 text-sm">Reviewing: <span className="text-indigo-400 font-mono">Chapter_145_Page_03.jpg</span></p>
                </div>
                <div className="flex gap-2 items-center">
                    <button
                        onClick={() => setIsEditorOpen(true)}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors mr-4"
                    >
                        <Edit3 className="w-4 h-4" />
                        Open Typesetter
                    </button>

                    <div className="flex gap-2 text-xs">
                        <span className="px-2 py-1 bg-slate-800 rounded text-slate-400">Resolution: 1400x2100</span>
                        <span className="px-2 py-1 bg-slate-800 rounded text-slate-400">Inpainting: Telea (Fast)</span>
                    </div>
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

            {/* Day 07: Editor Modal */}
            <EditorModal isOpen={isEditorOpen} onClose={() => setIsEditorOpen(false)}>
                <CanvasEditor />
            </EditorModal>
        </div>
    );
}
