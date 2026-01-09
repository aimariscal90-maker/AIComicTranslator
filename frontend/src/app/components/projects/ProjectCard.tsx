"use client";

import { motion } from "framer-motion";
import { Clock, FileImage, MoreVertical } from "lucide-react";
import Link from "next/link";

interface ProjectCardProps {
    id: string;
    title: string;
    coverUrl: string;
    pageCount: number;
    status: "completed" | "processing" | "draft";
    lastEdited: string;
}

const statusColors = {
    completed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    processing: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    draft: "bg-slate-500/10 text-slate-400 border-slate-500/20",
};

export default function ProjectCard({ id, title, coverUrl, pageCount, status, lastEdited }: ProjectCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="group relative bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-colors"
        >
            {/* Cover Image Area */}
            <div className="aspect-[2/3] bg-slate-950 relative overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                    src={coverUrl}
                    alt={title}
                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500"
                />

                {/* Overlay Gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-80" />

                {/* Status Badge */}
                <div className={`absolute top-3 left-3 px-2 py-0.5 rounded text-xs font-bold border backdrop-blur-md ${statusColors[status]}`}>
                    {status.toUpperCase()}
                </div>

                {/* Menu Button */}
                <button className="absolute top-3 right-3 p-1.5 bg-black/50 hover:bg-black/80 rounded text-white opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreVertical className="w-4 h-4" />
                </button>
            </div>

            {/* Info Content */}
            <div className="p-4 relative">
                <Link href={`/projects/${id}`} className="absolute inset-0 z-10" />

                <h3 className="font-bold text-white truncate group-hover:text-indigo-400 transition-colors">{title}</h3>

                <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                        <FileImage className="w-3 h-3" />
                        {pageCount} pages
                    </span>
                    <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {lastEdited}
                    </span>
                </div>

                {/* Progress Bar (Fake) */}
                <div className="mt-4 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                        className={`h-full rounded-full ${status === 'completed' ? 'bg-emerald-500 w-full' : status === 'processing' ? 'bg-indigo-500 w-1/2 animate-pulse' : 'bg-slate-600 w-1/5'}`}
                    />
                </div>
            </div>
        </motion.div>
    );
}
