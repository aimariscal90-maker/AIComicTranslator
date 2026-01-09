"use client";

import { useState, useEffect } from "react";
import ImageComparator from "@/app/components/cleaner/ImageComparator";
import CleanerToolbar from "@/app/components/cleaner/CleanerToolbar";
import EditorModal from "@/app/components/editor/EditorModal";
import CanvasEditor from "@/app/components/editor/CanvasEditor";
import { Edit3, ArrowLeft, Loader2 } from "lucide-react";
import { useSearchParams, useRouter } from "next/navigation";
import api from "@/services/api";
import { Job, ProcessingResult } from "@/types/api";
import { API_URL } from "@/config";
import Link from "next/link";
import { toast } from "sonner";

export default function CleanerPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const jobId = searchParams.get("job_id");

    // State
    const [isLoading, setIsLoading] = useState(true);
    const [result, setResult] = useState<ProcessingResult | null>(null);
    const [isEditorOpen, setIsEditorOpen] = useState(false);

    useEffect(() => {
        if (!jobId) return;

        const fetchData = async () => {
            try {
                const { data } = await api.get<Job>(`/jobs/${jobId}`);
                if (data.status === 'completed' && data.result) {
                    setResult(data.result);
                } else {
                    toast.error("Job incomplete or failed");
                }
            } catch (err) {
                toast.error("Failed to load job data");
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [jobId]);

    const getFullUrl = (path?: string) => {
        if (!path) return "";
        if (path.startsWith('http')) return path;
        const cleanPath = path.startsWith('/') ? path.substring(1) : path;
        return `${API_URL}/${cleanPath}`;
    };

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
            </div>
        );
    }

    if (!result) {
        return (
            <div className="flex h-screen items-center justify-center flex-col gap-4">
                <p className="text-slate-500">No Image Data Found</p>
                <Link href="/quick-translate" className="text-indigo-400 hover:underline">Go to Quick Translate</Link>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] relative">

            {/* Header / Context */}
            <div className="mb-4 flex justify-between items-end">
                <div className="flex items-center gap-4">
                    <Link href="/quick-translate" className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Magic Cleaner Workspace</h1>
                        <p className="text-slate-400 text-sm">Reviewing: <span className="text-indigo-400 font-mono">{result.filename}</span></p>
                    </div>
                </div>

                <div className="flex gap-2 items-center">
                    <button
                        onClick={() => setIsEditorOpen(true)}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold flex items-center gap-2 transition-colors shadow-lg shadow-indigo-500/20 mr-4"
                    >
                        <Edit3 className="w-4 h-4" />
                        Open Typesetter
                    </button>

                    <div className="flex gap-2 text-xs">
                        <span className="px-2 py-1 bg-slate-800 rounded text-slate-400">{result.bubbles_count} Bubbles Detected</span>
                        <span className="px-2 py-1 bg-slate-800 rounded text-slate-400">Fast Inpainting</span>
                    </div>
                </div>
            </div>

            {/* Main Workspace Canvas */}
            <div className="flex-1 relative bg-slate-950/50 rounded-xl overflow-hidden border border-slate-800 border-dashed flex items-center justify-center p-4">
                {/* Container for the comparator constrained to viewport to avoid scroll */}
                <div className="relative h-full aspect-[2/3] max-w-full shadow-2xl">
                    <ImageComparator
                        originalSrc={getFullUrl(result.original_url)}
                        cleanedSrc={getFullUrl(result.clean_url || result.final_url)} // Fallback if clean unavailable
                    />
                </div>
            </div>

            {/* Toolbar */}
            <CleanerToolbar />

            {/* Editor Modal */}
            <EditorModal isOpen={isEditorOpen} onClose={() => setIsEditorOpen(false)}>
                {/* Pass job data to editor */}
                <CanvasEditor
                    imageUrl={getFullUrl(result.clean_url || result.final_url)}
                    originalBubbles={result.bubbles_data}
                    filename={result.filename}
                />
            </EditorModal>
        </div>
    );
}
