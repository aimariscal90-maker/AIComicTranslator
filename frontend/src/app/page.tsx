"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Zap,
  Sparkles,
  GalleryVerticalEnd,
  ArrowRight,
  Clock,
  Plus,
  FileImage
} from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 }
};

export default function Dashboard() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Minimal Header */}
      <header className="flex items-end justify-between border-b border-slate-800 pb-6">
        <div>
          <motion.h1
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-3xl font-bold text-white tracking-tight"
          >
            Overview
          </motion.h1>
          <p className="text-slate-400 mt-1">Manage your scanlation pipeline.</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-white text-slate-950 rounded-lg text-sm font-bold hover:bg-slate-200 transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            New Project
          </button>
        </div>
      </header>

      {/* Bento Grid layout - Strict Dark Theme */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {/* 1. Quick Translate (Primary Action) */}
        <motion.div variants={item} className="md:col-span-2 group relative overflow-hidden rounded-xl bg-slate-900 border border-slate-800 p-8 transition-all hover:border-indigo-500/50 hover:shadow-[0_0_40px_-10px_rgba(99,102,241,0.1)]">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <Zap className="w-32 h-32 text-indigo-500 -rotate-12" />
          </div>

          <div className="relative z-10 h-full flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
                  <Zap className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-bold text-white">Quick Translate</h2>
              </div>
              <p className="text-slate-400 max-w-md">
                The fastest way to process a single page. Auto-detect bubbles, OCR, translate, and typeset in one go.
              </p>
            </div>

            <div className="mt-8 flex items-center gap-4">
              <Link href="/quick-translate" className="inline-flex items-center gap-2 text-indigo-400 font-bold hover:text-indigo-300 transition-colors">
                Start Pipeline <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </motion.div>

        {/* 2. Recent Projects Summary */}
        <motion.div variants={item} className="md:col-span-1 rounded-xl bg-slate-900 border border-slate-800 p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-slate-500" />
              Recent
            </h3>
          </div>

          <div className="flex-1 space-y-3">
            <div className="flex items-center gap-3 p-2 hover:bg-slate-800 rounded-lg cursor-pointer transition-colors group">
              <div className="w-10 h-14 bg-slate-950 rounded border border-slate-800 group-hover:border-slate-700 flex items-center justify-center">
                <FileImage className="w-4 h-4 text-slate-700" />
              </div>
              <div>
                <div className="text-sm font-medium text-slate-200">One Piece 1100</div>
                <div className="text-xs text-slate-500">Edited 20m ago</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-2 hover:bg-slate-800 rounded-lg cursor-pointer transition-colors group">
              <div className="w-10 h-14 bg-slate-950 rounded border border-slate-800 group-hover:border-slate-700 flex items-center justify-center">
                <FileImage className="w-4 h-4 text-slate-700" />
              </div>
              <div>
                <div className="text-sm font-medium text-slate-200">JJK 248</div>
                <div className="text-xs text-slate-500">Edited 1h ago</div>
              </div>
            </div>
          </div>

          <Link href="/projects" className="mt-4 text-xs text-center text-slate-500 hover:text-slate-300 py-2 border-t border-slate-800">
            View all projects
          </Link>
        </motion.div>

        {/* 3. Magic Cleaner (Secondary Tool) */}
        <motion.div variants={item} className="md:col-span-1 group rounded-xl bg-slate-900 border border-slate-800 p-6 flex flex-col hover:border-emerald-500/50 transition-colors cursor-pointer relative overflow-hidden">
          <div className="absolute top-4 right-4 text-emerald-500/10 group-hover:text-emerald-500/20 transition-colors">
            <Sparkles className="w-24 h-24" />
          </div>

          <div className="relative z-10">
            <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400 w-fit mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Magic Cleaner</h3>
            <p className="text-sm text-slate-400 mt-2 mb-8">
              Precision Inpainting tools. clean raw scans manually or review AI output with split-view comparison.
            </p>
            <Link href="/cleaner" className="mt-auto text-sm font-bold text-emerald-400 hover:text-emerald-300">
              Launch Tool
            </Link>
          </div>
        </motion.div>

        {/* 4. Stats / Library Info */}
        <motion.div variants={item} className="md:col-span-2 rounded-xl bg-slate-900 border border-slate-800 p-6 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="p-4 bg-slate-950 rounded-full border border-slate-800">
              <GalleryVerticalEnd className="w-6 h-6 text-slate-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Project Library</h3>
              <p className="text-sm text-slate-400">You have 12 active projects consuming 450MB.</p>
            </div>
          </div>
          <Link href="/projects" className="px-4 py-2 border border-slate-700 hover:bg-slate-800 rounded-lg text-sm font-medium text-white transition-colors">
            Manage Library
          </Link>
        </motion.div>
      </motion.div>

      {/* Legacy Link Minimal */}
      <div className="text-center pt-8">
        <Link href="/legacy-playground" className="text-[10px] uppercase tracking-widest text-slate-700 hover:text-slate-500 transition-colors">
          Legacy Playground
        </Link>
      </div>
    </div>
  );
}
