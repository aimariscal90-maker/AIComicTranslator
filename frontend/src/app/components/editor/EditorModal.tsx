"use client";

import { X, Save, Undo, Type } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect } from "react";

interface EditorModalProps {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

export default function EditorModal({ isOpen, onClose, children }: EditorModalProps) {
    // Lock body scroll
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
    }, [isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-4"
                >
                    <div className="w-full h-full max-w-[1600px] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
                        {/* Editor Toolbar */}
                        <div className="h-16 border-b border-slate-800 bg-slate-950 flex items-center justify-between px-6">
                            <div className="flex items-center gap-4">
                                <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                                    <X className="w-5 h-5" />
                                </button>
                                <span className="h-6 w-px bg-slate-800" />
                                <h2 className="text-white font-bold">Typesetter Studio</h2>
                            </div>

                            <div className="flex items-center gap-2">
                                <button className="px-3 py-1.5 bg-slate-800 text-slate-300 hover:text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
                                    <Undo className="w-4 h-4" /> Undo
                                </button>
                                <button className="px-3 py-1.5 bg-slate-800 text-slate-300 hover:text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
                                    <Type className="w-4 h-4" /> Global Font
                                </button>
                            </div>

                            <button className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all hover:scale-105">
                                <Save className="w-4 h-4" />
                                Save Changes
                            </button>
                        </div>

                        {/* Editor Canvas Area */}
                        <div className="flex-1 overflow-hidden relative bg-neutral-900 flex items-center justify-center p-8 cursor-crosshair">
                            {children}
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
