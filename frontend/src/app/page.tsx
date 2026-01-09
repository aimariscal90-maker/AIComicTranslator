"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Zap,
  Sparkles,
  GalleryVerticalEnd,
  ArrowRight,
  Clock
} from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export default function Dashboard() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <header className="space-y-2">
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-4xl font-bold tracking-tight text-white"
        >
          Welcome back, Creator
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="text-slate-400"
        >
          Here is what's happening with your projects today.
        </motion.p>
      </header>

      {/* Bento Grid */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {/* 1. Quick Translate (Main Feature) */}
        <motion.div variants={item} className="md:col-span-2 group relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 p-8 shadow-2xl transition-all hover:scale-[1.01] hover:shadow-indigo-500/25">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 h-64 w-64 rounded-full bg-white/10 blur-3xl opacity-50" />

          <div className="relative z-10 h-full flex flex-col justify-between">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white backdrop-blur-md">
                <Zap className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                <span>Fastest Workflow</span>
              </div>
              <h2 className="text-3xl font-bold text-white">Quick Translate</h2>
              <p className="max-w-md text-indigo-100">
                Drop a page, clean text, and translate in seconds. The automated pipeline for speed.
              </p>
            </div>

            <div className="mt-8">
              <Link href="/quick-translate" className="inline-flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-bold text-indigo-600 transition-colors hover:bg-indigo-50">
                Start New Translation
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </motion.div>

        {/* 2. Magic Cleaner */}
        <motion.div variants={item} className="group relative overflow-hidden rounded-2xl bg-slate-900 border border-slate-800 p-6 transition-all hover:border-slate-700 hover:shadow-xl">
          <div className="absolute inset-0 bg-transparent group-hover:bg-slate-800/50 transition-colors" />

          <div className="relative z-10 flex h-full flex-col">
            <div className="mb-4 h-12 w-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Magic Cleaner</h3>
            <p className="mt-2 text-sm text-slate-400">
              Remove text bubbles with precision using AI inpainting (LaMa/Telea).
            </p>
            <div className="mt-auto pt-6">
              <Link href="/cleaner" className="text-sm font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                Open Cleaner <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </motion.div>

        {/* 3. Recent Projects */}
        <motion.div variants={item} className="md:col-span-1 row-span-2 rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="flex items-center gap-2 font-bold text-white">
              <Clock className="h-5 w-5 text-slate-500" />
              Recent Activity
            </h3>
            <Link href="/projects" className="text-xs text-indigo-400 hover:text-indigo-300">View All</Link>
          </div>

          <div className="flex-1 space-y-4">
            {/* Mock Items */}
            <div className="group flex items-center gap-3 rounded-lg p-2 hover:bg-slate-800/50 transition-colors cursor-pointer">
              <div className="h-10 w-10 bg-slate-800 rounded-md shrink-0 border border-slate-700" />
              <div className="min-w-0 flex-1">
                <h4 className="truncate text-sm font-medium text-slate-200 group-hover:text-white">Chapter 145 RAW</h4>
                <p className="text-xs text-slate-500">Edited 2 hours ago</p>
              </div>
            </div>
            <div className="group flex items-center gap-3 rounded-lg p-2 hover:bg-slate-800/50 transition-colors cursor-pointer">
              <div className="h-10 w-10 bg-slate-800 rounded-md shrink-0 border border-slate-700" />
              <div className="min-w-0 flex-1">
                <h4 className="truncate text-sm font-medium text-slate-200 group-hover:text-white">One Piece 1099</h4>
                <p className="text-xs text-slate-500">Edited 5 hours ago</p>
              </div>
            </div>
            <div className="group flex items-center gap-3 rounded-lg p-2 hover:bg-slate-800/50 transition-colors cursor-pointer">
              <div className="h-10 w-10 bg-slate-800 rounded-md shrink-0 border border-slate-700" />
              <div className="min-w-0 flex-1">
                <h4 className="truncate text-sm font-medium text-slate-200 group-hover:text-white">Project Alpha</h4>
                <p className="text-xs text-slate-500">Edited yesterday</p>
              </div>
            </div>
            {/* Empty State Mock */}
            <div className="h-full flex items-center justify-center border-2 border-dashed border-slate-800 rounded-lg p-4 opacity-50">
              <span className="text-xs text-slate-600">No more history</span>
            </div>
          </div>
        </motion.div>

        {/* 4. Project Manager / Library */}
        <motion.div variants={item} className="md:col-span-2 rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col justify-between">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <GalleryVerticalEnd className="text-slate-500" />
                Project Library
              </h3>
              <p className="mt-1 text-sm text-slate-400">Manage your volumes and chapters.</p>
            </div>
            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-bold text-slate-300">
              12 Projects
            </span>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-slate-950 rounded text-xs text-slate-400 border border-slate-800">Completed: 4</span>
            <span className="px-2 py-1 bg-slate-950 rounded text-xs text-slate-400 border border-slate-800">In Progress: 2</span>
            <span className="px-2 py-1 bg-slate-950 rounded text-xs text-slate-400 border border-slate-800">Drafts: 6</span>
          </div>
        </motion.div>
      </motion.div>

      {/* Quick Actions Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex justify-center pt-8 opacity-50 hover:opacity-100 transition-opacity"
      >
        <Link href="/legacy-playground" className="text-xs text-slate-600 hover:text-slate-400 underline">
          Access Legacy Playground
        </Link>
      </motion.div>
    </div>
  );
}
