"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Maximize2, ZoomIn } from "lucide-react";

interface DualPanelViewProps {
    originalSrc: string | null;
    resultSrc: string | null;
    isProcessing: boolean;
}

export default function DualPanelView({ originalSrc, resultSrc, isProcessing }: DualPanelViewProps) {
    const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);

    return (
        <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
                {/* Left Panel: Original */}
                <Panel
                    title="Input Source"
                    src={originalSrc}
                    placeholder="Waiting for upload..."
                    onExpand={() => originalSrc && setLightboxSrc(originalSrc)}
                />

                {/* Right Panel: Result */}
                <Panel
                    title="Result"
                    src={resultSrc}
                    isActive={!!resultSrc}
                    isLoading={isProcessing}
                    placeholder="Result will appear here"
                    headerColor="text-emerald-400"
                    onExpand={() => resultSrc && setLightboxSrc(resultSrc)}
                />
            </div>

            {/* Lightbox Overlay */}
            <AnimatePresence>
                {lightboxSrc && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setLightboxSrc(null)}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-xl p-8 cursor-zoom-out"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                            className="relative max-w-full max-h-full"
                            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking image
                        >
                            <button
                                onClick={() => setLightboxSrc(null)}
                                className="absolute -top-12 right-0 p-2 bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors"
                            >
                                <X className="w-6 h-6" />
                            </button>

                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                                src={lightboxSrc}
                                alt="Fullscreen Preview"
                                className="max-w-[95vw] max-h-[90vh] object-contain rounded-lg shadow-2xl shadow-black"
                            />
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}

// Sub-component for cleaner code
function Panel({
    title,
    src,
    isActive = false,
    isLoading = false,
    placeholder,
    headerColor = "text-slate-400",
    onExpand
}: {
    title: string;
    src: string | null;
    isActive?: boolean;
    isLoading?: boolean;
    placeholder: string;
    headerColor?: string;
    onExpand: () => void;
}) {
    return (
        <div className="bg-slate-900/40 rounded-3xl border border-white/5 p-1 flex flex-col group/panel overflow-hidden relative">

            {/* Header */}
            <div className="absolute top-4 left-6 z-10 flex w-[calc(100%-3rem)] justify-between items-center pointer-events-none">
                <h3 className={`font-bold text-xs uppercase tracking-widest ${headerColor}`}>{title}</h3>
                {isLoading && <span className="text-xs text-indigo-400 font-mono animate-pulse">Processing...</span>}
            </div>

            <div className={`flex-1 rounded-[1.2rem] bg-slate-950/50 overflow-hidden flex items-center justify-center relative border border-white/5 ${src ? 'cursor-zoom-in' : ''}`} onClick={onExpand}>
                {src ? (
                    <>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={src} alt={title} className="max-w-full max-h-full object-contain transition-transform duration-500 group-hover/panel:scale-[1.02]" />

                        {/* Hover Overlay Hint */}
                        <div className="absolute inset-0 bg-black/0 group-hover/panel:bg-black/20 transition-all flex items-center justify-center opacity-0 group-hover/panel:opacity-100 backdrop-blur-[0px] group-hover/panel:backdrop-blur-[2px]">
                            <div className="bg-black/60 px-4 py-2 rounded-full text-white text-sm font-bold flex items-center gap-2 transform translate-y-4 group-hover/panel:translate-y-0 transition-all">
                                <Maximize2 className="w-4 h-4" /> Expand
                            </div>
                        </div>
                    </>
                ) : isLoading ? (
                    <div className="w-full h-full flex items-center justify-center">
                        <div className="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                    </div>
                ) : (
                    <div className="text-slate-600 font-medium flex flex-col items-center gap-2">
                        <ZoomIn className="w-8 h-8 opacity-20" />
                        {placeholder}
                    </div>
                )}
            </div>
        </div>
    );
}
