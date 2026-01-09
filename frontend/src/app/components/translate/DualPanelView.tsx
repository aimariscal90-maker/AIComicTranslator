"use client";

import { motion } from "framer-motion";

interface DualPanelViewProps {
    originalSrc: string | null;
    resultSrc: string | null;
    isProcessing: boolean;
}

export default function DualPanelView({ originalSrc, resultSrc, isProcessing }: DualPanelViewProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
            {/* Left Panel: Original */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 flex flex-col">
                <h3 className="text-white font-bold mb-4 opacity-50 text-sm uppercase tracking-wider">Input Source</h3>
                <div className="flex-1 rounded-lg bg-black/50 overflow-hidden flex items-center justify-center relative">
                    {originalSrc ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={originalSrc} alt="Original" className="max-w-full max-h-full object-contain" />
                    ) : (
                        <div className="text-slate-600 text-sm">Waiting for upload...</div>
                    )}
                </div>
            </div>

            {/* Right Panel: Result */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 flex flex-col">
                <h3 className="text-emerald-400 font-bold mb-4 opacity-90 text-sm uppercase tracking-wider flex justify-between">
                    <span>Result</span>
                    {isProcessing && <span className="animate-pulse">Generating...</span>}
                </h3>

                <div className="flex-1 rounded-lg bg-black/50 overflow-hidden flex items-center justify-center relative">
                    {resultSrc ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={resultSrc} alt="Result" className="max-w-full max-h-full object-contain" />
                    ) : isProcessing ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                            {/* Skeleton Loading Effect */}
                            <div className="w-3/4 h-3/4 bg-slate-800/50 rounded animate-pulse" />
                        </div>
                    ) : (
                        <div className="text-slate-600 text-sm">Result will appear here</div>
                    )}
                </div>
            </div>
        </div>
    );
}
