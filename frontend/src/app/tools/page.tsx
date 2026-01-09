"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
    Eraser,
    Package,
    FileUp,
    ZoomIn,
    Wand2,
    Image as ImageIcon,
    FileType,
    ArrowRight
} from "lucide-react";

const tools = [
    {
        id: "cleaner",
        title: "Text Remover",
        description: "Remove text bubbles from manga pages automatically without translating.",
        icon: Eraser,
        color: "bg-pink-500",
        href: "/tools/text-remover",
        status: "Ready"
    },
    {
        id: "packer",
        title: "Comic Packer",
        description: "Convert valid image sequences into .CBZ or .PDF files for readers.",
        icon: Package,
        color: "bg-amber-500",
        href: "/tools/packer",
        status: "Coming Soon"
    },
    {
        id: "extract",
        title: "Extract Pages",
        description: "Extract high-quality images from PDF or CBZ files per chapter.",
        icon: FileUp,
        color: "bg-cyan-500",
        href: "/tools/extract",
        status: "Coming Soon"
    },
    {
        id: "upscale",
        title: "Smart Upscale",
        description: "Increase resolution of anime/manga art using AI super-resolution.",
        icon: ZoomIn,
        color: "bg-violet-500",
        href: "/tools/upscale",
        status: "Planned"
    }
];

export default function ToolsPage() {
    return (
        <div className="max-w-7xl mx-auto space-y-12">

            {/* Header */}
            <div className="text-center space-y-4 py-10">
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl font-extrabold text-white tracking-tight"
                >
                    The <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Toolkit</span>
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="text-xl text-slate-400 max-w-2xl mx-auto"
                >
                    Specialized utilities for every step of the scanlation process.
                    Simple, fast, and powerful.
                </motion.p>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 px-4">
                {tools.map((tool, index) => (
                    <motion.div
                        key={tool.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.1 }}
                        whileHover={{ y: -5 }}
                        className="group relative bg-slate-900 border border-slate-800 rounded-3xl p-8 hover:bg-slate-800/50 hover:border-indigo-500/30 transition-all cursor-pointer overflow-visible"
                    >
                        {/* Glow Effect */}
                        <div className={`absolute top-0 right-0 w-32 h-32 ${tool.color} blur-[80px] opacity-10 group-hover:opacity-20 transition-opacity rounded-full pointer-events-none`} />

                        <div className="relative z-10 flex flex-col h-full">
                            <div className={`w-14 h-14 ${tool.color} rounded-2xl flex items-center justify-center text-white shadow-lg mb-6 group-hover:scale-110 transition-transform`}>
                                <tool.icon className="w-7 h-7" />
                            </div>

                            <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-indigo-400 transition-colors">
                                {tool.title}
                            </h3>

                            <p className="text-slate-400 leading-relaxed mb-6 flex-1">
                                {tool.description}
                            </p>

                            <div className="flex items-center justify-between mt-auto">
                                <span className={`text-xs font-bold px-3 py-1 rounded-full ${tool.status === 'Ready' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-700/50 text-slate-500'
                                    }`}>
                                    {tool.status}
                                </span>

                                {tool.status === 'Ready' && (
                                    <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0">
                                        <ArrowRight className="w-4 h-4" />
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                ))}

                {/* Coming Soon Placeholder */}
                <div className="md:col-span-2 lg:col-span-1 border-2 border-dashed border-slate-800 rounded-3xl flex flex-col items-center justify-center p-8 text-slate-600">
                    <Wand2 className="w-10 h-10 mb-4 opacity-50" />
                    <p className="font-bold">More coming soon...</p>
                    <p className="text-sm">Have a suggestion?</p>
                </div>
            </div>
        </div>
    );
}
