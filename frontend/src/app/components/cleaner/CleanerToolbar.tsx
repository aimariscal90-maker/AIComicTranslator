"use client";

import { motion } from "framer-motion";
import {
    Download,
    Eraser,
    Eye,
    EyeOff,
    RotateCcw,
    Undo,
    ZoomIn,
    ZoomOut
} from "lucide-react";

export default function CleanerToolbar() {
    return (
        <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50"
        >
            <div className="flex items-center gap-2 p-2 bg-slate-900/90 backdrop-blur-xl border border-slate-700 rounded-full shadow-2xl">

                <div className="flex items-center gap-1 px-2 border-r border-slate-700">
                    <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-full transition-colors" title="Zoom Out">
                        <ZoomOut className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-full transition-colors" title="Zoom In">
                        <ZoomIn className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex items-center gap-1 px-2 border-r border-slate-700">
                    <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-full transition-colors" title="Undo">
                        <Undo className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-full transition-colors" title="Reset View">
                        <RotateCcw className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex items-center gap-1 px-2">
                    <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full font-medium transition-colors">
                        <Eraser className="w-4 h-4" />
                        <span>Process Page</span>
                    </button>

                    <button className="p-2 text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 rounded-full transition-colors" title="Download Result">
                        <Download className="w-5 h-5" />
                    </button>
                </div>

            </div>
        </motion.div>
    );
}
