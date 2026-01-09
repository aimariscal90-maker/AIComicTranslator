"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Zap,
  Sparkles,
  GalleryVerticalEnd,
  ArrowRight,
  Plus,
  FileImage,
  TrendingUp,
  Loader2
} from "lucide-react";
import api from "@/services/api";
import { Project } from "@/types/api";

// Animation Variants
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 50 }
  }
};

export default function Dashboard() {
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecent = async () => {
      try {
        const { data } = await api.get<Project[]>('/projects');
        setRecentProjects(data.slice(0, 3));
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecent();
  }, []);

  return (
    <div className="space-y-10 max-w-7xl mx-auto relative z-10">
      {/* Ambient Background Glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Header Section */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-1">
          <motion.h1
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-4xl font-extrabold text-white tracking-tight"
          >
            Good Evening, Creator
          </motion.h1>
          <p className="text-slate-400 text-lg">
            Ready to translate some comics today?
          </p>
        </div>

        <Link href="/projects">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full text-sm font-bold shadow-lg shadow-indigo-500/25 flex items-center gap-2 transition-all"
          >
            <Plus className="w-5 h-5" />
            New Project
          </motion.button>
        </Link>
      </header>

      {/* Bento Grid layout */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-12 gap-6"
      >
        {/* 1. Feature Card: Quick Translate (Large) */}
        <motion.div variants={item} className="col-span-1 md:col-span-8 group relative overflow-hidden rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl p-8 hover:bg-slate-900/60 transition-colors">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

          <div className="relative z-10 flex flex-col h-full justify-between">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-indigo-500 rounded-2xl text-white shadow-lg shadow-indigo-500/20">
                  <Zap className="w-6 h-6" />
                </div>
                <h2 className="text-2xl font-bold text-white">Quick Translate</h2>
              </div>
              <p className="text-slate-300 text-lg max-w-xl leading-relaxed">
                Experience the lightning-fast workflow. Drop a raw page, and let our AI pipeline handle detection, OCR, and cleaning in seconds.
              </p>
            </div>

            <div className="mt-8">
              <Link href="/quick-translate" className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-white text-slate-950 font-bold hover:bg-indigo-50 transition-colors">
                Launch Pipeline <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>

          {/* Decor Image/Icon */}
          <Zap className="absolute -bottom-10 -right-10 w-64 h-64 text-white/5 rotate-12" />
        </motion.div>

        {/* 2. Stat Card: Activity */}
        <motion.div variants={item} className="col-span-1 md:col-span-4 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl p-6 flex flex-col justify-between hover:border-white/10 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
                Activity
              </h3>
              <span className="text-xs text-emerald-400 font-mono bg-emerald-500/10 px-2 py-1 rounded-full">Live</span>
            </div>
            <div className="h-24 flex items-end gap-1">
              {/* Fake Chart for Animation */}
              {[40, 60, 30, 80, 50, 90, 60].map((h, i) => (
                <div key={i} className="flex-1 bg-slate-700/50 hover:bg-indigo-500 rounded-t-sm transition-colors" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-4">
            System operational.
          </p>
        </motion.div>

        {/* 3. Feature Card: Magic Cleaner */}
        <motion.div variants={item} className="col-span-1 md:col-span-5 group rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl p-8 hover:bg-slate-900/60 transition-colors relative overflow-hidden">
          <div className="relative z-10">
            <div className="p-3 bg-emerald-500/20 rounded-2xl text-emerald-400 w-fit mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Magic Cleaner</h3>
            <p className="text-slate-400 mb-6">
              Precision tools for manual cleanup and inpainting verification. Access via Projects.
            </p>
            <Link href="/projects" className="text-emerald-400 font-bold hover:text-emerald-300 flex items-center gap-2 group-hover:gap-3 transition-all">
              Go to Projects <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </motion.div>

        {/* 4. Recent Projects List */}
        <motion.div variants={item} className="col-span-1 md:col-span-7 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl p-8 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <GalleryVerticalEnd className="w-5 h-5 text-slate-400" />
              Recent Projects
            </h3>
            <Link href="/projects" className="text-sm text-indigo-400 hover:text-indigo-300">View All</Link>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="py-4 text-center">
                <Loader2 className="w-6 h-6 animate-spin text-slate-600 mx-auto" />
              </div>
            ) : recentProjects.length === 0 ? (
              <div className="text-slate-500 text-sm py-4 text-center">
                No projects yet. Create one above!
              </div>
            ) : (
              recentProjects.map((project, i) => (
                <Link href={`/projects/${project.id}`} key={i} className="flex items-center justify-between p-3 rounded-2xl hover:bg-white/5 transition-colors group cursor-pointer">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-slate-500 group-hover:text-white transition-colors">
                      <FileImage className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-200 group-hover:text-white">{project.name}</h4>
                      <p className="text-xs text-slate-500 flex items-center gap-2">
                        {new Date(project.created_at || Date.now()).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="px-3 py-1 rounded-full text-xs font-bold bg-slate-700/30 text-slate-400">
                    {project.pages?.length || 0} Pages
                  </div>
                </Link>
              ))
            )}
          </div>
        </motion.div>
      </motion.div>

      {/* Footer Links */}
      <motion.div variants={item} className="flex justify-center pt-6 opacity-30 hover:opacity-100 transition-opacity">
        <Link href="/legacy-playground" className="text-xs text-white">
          Legacy Playground (Debug)
        </Link>
      </motion.div>
    </div>
  );
}
