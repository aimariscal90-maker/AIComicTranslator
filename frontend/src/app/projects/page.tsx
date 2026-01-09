"use client";

import { useState } from "react";
import ProjectCard from "@/app/components/projects/ProjectCard";
import { Filter, FolderPlus, Search } from "lucide-react";

// Mock Data
const MOCK_PROJECTS = [
    { id: "1", title: "One Piece Ch. 1100", cover: "https://placehold.co/400x600/222/FFF/png?text=OP+1100", pages: 19, status: "completed", date: "2h ago" },
    { id: "2", title: "Jujutsu Kaisen Ch. 248", cover: "https://placehold.co/400x600/333/FFF/png?text=JJK+248", pages: 21, status: "processing", date: "5m ago" },
    { id: "3", title: "Chainsaw Man Ch. 155", cover: "https://placehold.co/400x600/444/FFF/png?text=CSM+155", pages: 18, status: "draft", date: "1d ago" },
    { id: "4", title: "Kagurabachi Vol 1", cover: "https://placehold.co/400x600/222/FFF/png?text=Kagura", pages: 45, status: "completed", date: "3d ago" },
    { id: "5", title: "Dandadan Ch. 140", cover: "https://placehold.co/400x600/555/FFF/png?text=Dandan", pages: 22, status: "draft", date: "1w ago" },
];

export default function ProjectsPage() {
    const [filter, setFilter] = useState("all");

    // @ts-ignore
    const filteredProjects = MOCK_PROJECTS.filter(p => filter === 'all' || p.status === filter);

    return (
        <div className="space-y-8">
            {/* Header / Actions */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white">Library</h1>
                    <p className="text-slate-400">Manage your translation projects.</p>
                </div>

                <div className="flex gap-2 w-full md:w-auto">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search projects..."
                            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:ring-1 focus:ring-indigo-500 outline-none"
                        />
                    </div>
                    <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 whitespace-nowrap">
                        <FolderPlus className="w-4 h-4" />
                        New Project
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
                <button
                    onClick={() => setFilter('all')}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'all' ? 'bg-white text-slate-900' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                >
                    All Projects
                </button>
                <button
                    onClick={() => setFilter('processing')}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'processing' ? 'bg-indigo-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                >
                    In Progress
                </button>
                <button
                    onClick={() => setFilter('completed')}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'completed' ? 'bg-emerald-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                >
                    Completed
                </button>
                <button
                    onClick={() => setFilter('draft')}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'draft' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                >
                    Drafts
                </button>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {filteredProjects.map((project) => (
                    // @ts-ignore
                    <ProjectCard
                        key={project.id}
                        id={project.id}
                        title={project.title}
                        coverUrl={project.cover}
                        pageCount={project.pages}
                        // @ts-ignore
                        status={project.status}
                        lastEdited={project.date}
                    />
                ))}
            </div>
        </div>
    );
}
