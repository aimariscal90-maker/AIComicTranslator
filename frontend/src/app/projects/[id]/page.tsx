"use client";

import { useState, useEffect, use } from "react";
import { useParams } from "next/navigation";
import api from "@/services/api";
import { Project, ComicPage } from "@/types/api";
import { toast } from "sonner";
import { Loader2, Plus, ArrowLeft, Image as ImageIcon, Download } from "lucide-react";
import Link from "next/link";
import { API_URL } from "@/config";
import SmartDropzone from "@/app/components/upload/SmartDropzone";
import { usePolling } from "@/hooks/usePolling";

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const resolvedParams = use(params);
    const id = resolvedParams.id;

    const [project, setProject] = useState<Project | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        fetchProject();
    }, [id]);

    const fetchProject = async () => {
        try {
            const { data } = await api.get<Project>(`/projects/${id}`);
            setProject(data);
        } catch (err) {
            toast.error("Failed to load project");
        } finally {
            setIsLoading(false);
        }
    };

    const handleUpload = async (file: File) => {
        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', id);

        try {
            toast.message("Uploading page...");
            const { data } = await api.post('/process', formData);
            toast.success("Page added to processing queue");
            // Ideally start polling here or just reload project after a delay
            // For MVP, just reloading project list to show 'processing' if we supported status
            // But currently Pages link to Job ID only implicitly? 
            // Wait, backend `process_comic_task` creates a `Page` entity.

            setTimeout(fetchProject, 2000); // Quick refresh hack
        } catch (err) {
            toast.error("Failed to upload page");
        } finally {
            setIsUploading(false);
        }
    };

    if (isLoading) return <div className="p-10 text-center"><Loader2 className="animate-spin mx-auto text-white" /></div>;
    if (!project) return <div className="p-10 text-center text-white">Project not found</div>;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/projects" className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors">
                    <ArrowLeft className="w-5 h-5" />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold text-white">{project.name}</h1>
                    <p className="text-slate-400">{project.description || "No description"} • {project.pages?.length || 0} Pages</p>
                </div>
                <div className="ml-auto flex gap-4">
                    <div className="flex bg-slate-800 rounded-lg p-1 h-fit my-auto">
                        <a
                            href={`${API_URL}/projects/${id}/export?format=cbz`}
                            target="_blank"
                            className="px-3 py-1.5 hover:bg-slate-700 rounded text-xs font-bold text-white transition-colors flex items-center gap-1"
                        >
                            <Download className="w-3 h-3" /> CBZ
                        </a>
                        <div className="w-[1px] bg-white/10 my-1"></div>
                        <a
                            href={`${API_URL}/projects/${id}/export?format=zip`}
                            target="_blank"
                            className="px-3 py-1.5 hover:bg-slate-700 rounded text-xs font-bold text-white transition-colors flex items-center gap-1"
                        >
                            ZIP
                        </a>
                    </div>
                    <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 shadow-lg">
                        <Plus className="w-4 h-4" /> Add Page
                    </button>
                </div>
            </div>

            {/* Upload Area (Collapsible or always visible?) */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-widest">Upload New Page</h3>
                <div className="h-40">
                    <SmartDropzone onFileSelect={handleUpload} />
                </div>
            </div>

            {/* Pages Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                {project.pages?.map((page: any) => (
                    <Link href={`/cleaner?job_id=${page.filename}`} key={page.id} className="group relative aspect-[2/3] bg-slate-950 rounded-lg overflow-hidden border border-slate-800 hover:border-indigo-500 transition-all hover:-translate-y-1 block cursor-pointer">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                            src={`${API_URL}${page.final_url || page.original_url}`}
                            alt={`Page ${page.page_number}`}
                            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                        />
                        <div className="absolute bottom-0 left-0 right-0 bg-black/80 p-2 text-xs font-mono text-center text-white">
                            Page {page.page_number || "?"}
                        </div>
                    </Link>
                ))}

                {(!project.pages || project.pages.length === 0) && (
                    <div className="col-span-full py-10 text-center text-slate-500">
                        No pages yet. Upload one above!
                    </div>
                )}
            </div>
        </div>
    );
}
