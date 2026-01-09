"use client";

import { useState, useCallback } from "react";
import PipelineStepper from "@/app/components/translate/PipelineStepper";
import DualPanelView from "@/app/components/translate/DualPanelView";
import SmartDropzone from "@/app/components/upload/SmartDropzone";
import { ArrowLeft, Download, AlertCircle, RefreshCw, Edit3 } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import api from "@/services/api";
import { usePolling } from "@/hooks/usePolling";
import { API_URL } from "@/config";
import { Job } from "@/types/api";

export default function QuickTranslatePage() {
    const [file, setFile] = useState<File | null>(null);
    const [currentStepId, setCurrentStepId] = useState("idle");
    const [originalUrl, setOriginalUrl] = useState<string | null>(null);
    const [resultUrl, setResultUrl] = useState<string | null>(null);

    // Polling Hook
    const { startPolling, stopPolling, isPolling, job, error } = usePolling({
        onProgress: (updatedJob) => {
            // Map percentage to Visual Steps for Stepper
            const p = updatedJob.progress;
            if (p < 20) setCurrentStepId("upload");
            else if (p < 40) setCurrentStepId("detect");
            else if (p < 50) setCurrentStepId("ocr");
            else if (p < 70) setCurrentStepId("translate");
            else if (p < 100) setCurrentStepId("render");
            else setCurrentStepId("completed");
        },
        onComplete: (completedJob) => {
            setCurrentStepId("completed");
            if (completedJob.result?.final_url) {
                setResultUrl(getFullUrl(completedJob.result.final_url));
            }
            toast.success("Translation Complete!", {
                description: "Your page is ready.",
                duration: 5000,
            });
        },
        onFail: (errMsg) => {
            setCurrentStepId("failed");
            toast.error("Processing Failed", { description: errMsg });
        }
    });

    const getFullUrl = (path: string) => {
        if (path.startsWith('http')) return path;
        // Remove leading slash if needed
        const cleanPath = path.startsWith('/') ? path.substring(1) : path;
        return `${API_URL}/${cleanPath}`;
    };

    const handleFileSelect = async (uploadedFile: File) => {
        setFile(uploadedFile);
        setCurrentStepId("upload");
        setOriginalUrl(URL.createObjectURL(uploadedFile)); // Preview local immediately
        setResultUrl(null);

        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            toast.message("Uploading...", { description: "Sending file to secure server." });
            const { data } = await api.post<{ job_id: string }>('/process', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            toast.message("Processing Started", { description: "AI Pipeline active." });
            startPolling(data.job_id);

        } catch (err: any) {
            console.error(err);
            toast.error("Upload Failed", {
                description: err.response?.data?.detail || "Network error"
            });
            setCurrentStepId("idle");
            setFile(null);
        }
    };

    const resetPipeline = () => {
        stopPolling();
        setFile(null);
        setCurrentStepId("idle");
        setOriginalUrl(null);
        setResultUrl(null);
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] gap-6">

            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/" className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                            <span className="text-indigo-400">⚡</span> Quick Translate Pipeline
                        </h1>
                        {isPolling && job && (
                            <p className="text-xs text-indigo-400 animate-pulse font-mono">
                                Step: {job.step} ({job.progress}%)
                            </p>
                        )}
                    </div>
                </div>

                {currentStepId === 'completed' && resultUrl && (
                    <div className="flex gap-2">
                        <button
                            onClick={resetPipeline}
                            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-bold shadow-sm transition-colors flex items-center gap-2"
                        >
                            <RefreshCw className="w-4 h-4" /> New
                        </button>

                        <Link
                            href={`/cleaner?job_id=${job?.id}`}
                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2"
                        >
                            <Edit3 className="w-4 h-4" /> Open Editor
                        </Link>

                        <a
                            href={resultUrl}
                            download
                            target="_blank"
                            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-bold shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2"
                        >
                            <Download className="w-4 h-4" /> Download
                        </a>
                    </div>
                )}
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-center gap-3 text-red-400">
                    <AlertCircle className="w-5 h-5" />
                    <div>
                        <p className="font-bold">Processing Error</p>
                        <p className="text-sm">{error}</p>
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            {!file ? (
                // State: Upload (Empty)
                <div className="flex-1 flex items-center justify-center p-12 animate-in fade-in zoom-in-95 duration-500">
                    <div className="w-full max-w-2xl h-80">
                        <SmartDropzone onFileSelect={handleFileSelect} />
                    </div>
                </div>
            ) : (
                // State: Processing / Result
                <div className="flex-1 flex gap-6 min-h-0 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Left: Pipeline Status (Sticky) */}
                    <div className="w-72 shrink-0 bg-slate-900/40 p-6 rounded-xl border border-white/5 backdrop-blur-sm h-fit">
                        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6 border-b border-white/5 pb-2">
                            Pipeline Status
                        </h2>
                        <PipelineStepper currentStepId={currentStepId} />
                    </div>

                    {/* Right: Dual View */}
                    <div className="flex-1 min-w-0">
                        <DualPanelView
                            originalSrc={originalUrl}
                            resultSrc={resultUrl}
                            isProcessing={isPolling}
                        />
                    </div>
                </div>
            )}

        </div>
    );
}
