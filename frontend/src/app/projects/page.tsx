"use client";

import { useState, useEffect } from "react";
import ProjectCard from "@/app/components/projects/ProjectCard";
import { Filter, FolderPlus, Search, Loader2 } from "lucide-react";
import api from "@/services/api";
import { Project } from "@/types/api"; // Ensure this type exists
import { API_URL } from "@/config";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function ProjectsPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filter, setFilter] = useState("all");
    const [searchTerm, setSearchTerm] = useState("");
    const router = useRouter();

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const { data } = await api.get<Project[]>('/projects');
            setProjects(data);
        } catch (err) {
            toast.error("Failed to load projects");
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateProject = async () => {
        // Simple prompt for MVP (Can be modal later)
        const name = prompt("Enter project name:"); // Temporary UX
        if (!name) return;

        try {
            const { data } = await api.post<Project>('/projects', { name });
            toast.success("Project created!");
            setProjects([data, ...projects]);
            router.push(`/projects/${data.id}`); // Go to detail
        } catch (err) {
            toast.error("Failed to create project");
        }
    };

    const getProjectCover = (project: Project) => {
        if (project.pages && project.pages.length > 0) {
            const firstPage = project.pages[0];
            const url = firstPage.final_url || firstPage.original_url || "";
            if (url.startsWith("/")) return `${API_URL}${url}`;
            return url;
        }
        return `https://placehold.co/400x600/1e293b/475569/png?text=${encodeURIComponent(project.name)}`;
    };

    const getStatus = (project: Project): "completed" | "processing" | "draft" => {
        if (!project.pages || project.pages.length === 0) return "draft";
        const allCompleted = project.pages.every((p: any) => p.status === 'completed');
        if (allCompleted) return "completed";
        return "processing";
    };

    const filteredProjects = projects.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase());
        const status = getStatus(p);
        const matchesFilter = filter === 'all' || status === filter;
        return matchesSearch && matchesFilter;
    });

    if (isLoading) {
        return (
            <div className="flex h-[calc(100vh-6rem)] items-center justify-center">
                <Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
            </div>
        );
    }

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
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:ring-1 focus:ring-indigo-500 outline-none"
                        />
                    </div>
                    <button
                        onClick={handleCreateProject}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 whitespace-nowrap shadow-lg shadow-indigo-500/20"
                    >
                        <FolderPlus className="w-4 h-4" />
                        New Project
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
                <button onClick={() => setFilter('all')} className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'all' ? 'bg-white text-slate-900' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>All Projects</button>
                <button onClick={() => setFilter('processing')} className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'processing' ? 'bg-indigo-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>In Progress</button>
                <button onClick={() => setFilter('completed')} className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'completed' ? 'bg-emerald-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>Completed</button>
                <button onClick={() => setFilter('draft')} className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'draft' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>Drafts</button>
            </div>

            {/* Grid */}
            {filteredProjects.length === 0 ? (
                <div className="text-center py-20 text-slate-500 border border-dashed border-slate-800 rounded-xl">
                    <p>No projects found. Create one to get started!</p>
                </div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {filteredProjects.map((project) => (
                        <ProjectCard
                            key={project.id}
                            id={project.id}
                            title={project.name}
                            coverUrl={getProjectCover(project)}
                            pageCount={project.pages ? project.pages.length : 0}
                            status={getStatus(project)}
                            lastEdited={new Date(project.created_at || Date.now()).toLocaleDateString()}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
