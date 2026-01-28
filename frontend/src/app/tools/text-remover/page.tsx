"use client";

import { useState } from "react";
import SmartDropzone from "@/app/components/upload/SmartDropzone";
import ImageComparator from "@/app/components/cleaner/ImageComparator";
import { ArrowLeft, Download, Eraser, Loader2, Sparkles } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import api from "@/services/api";
import { usePolling } from "@/hooks/usePolling";
import { API_URL } from "@/config";

export default function TextRemoverPage() {
    const [file, setFile] = useState<File | null>(null);
    const [originalUrl, setOriginalUrl] = useState<string | null>(null);
    const [resultUrl, setResultUrl] = useState<string | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);

    const [showMetrics, setShowMetrics] = useState(false);

    const { startPolling, job, stopPolling } = usePolling({
        onComplete: (completedJob) => {
            setIsProcessing(false);
            if (completedJob.result?.final_url) {
                setResultUrl(getFullUrl(completedJob.result.final_url));
            }
            setShowMetrics(true);
            toast.success("Text Removed Successfully!");
        },
        onFail: (err) => {
            setIsProcessing(false);
            toast.error("Cleanup Failed", { description: err });
        }
    });

    const getFullUrl = (path: string) => {
        if (path.startsWith('http')) return path;
        const cleanPath = path.startsWith('/') ? path.substring(1) : path;
        return `${API_URL}/${cleanPath}`;
    };

    const [cleaningStrategy, setCleaningStrategy] = useState<'clean_text' | 'remove_bubble'>('clean_text');

    const handleFileSelect = async (uploadedFile: File) => {
        setFile(uploadedFile);
        setOriginalUrl(URL.createObjectURL(uploadedFile));
        setResultUrl(null);
        setIsProcessing(true);
        setShowMetrics(false);

        const formData = new FormData();
        formData.append('file', uploadedFile);
        formData.append('mode', 'clean_only');
        formData.append('cleaning_strategy', cleaningStrategy);

        try {
            toast.message("Uploading & Scrubbing...");
            const { data } = await api.post<{ job_id: string }>('/process', formData);
            startPolling(data.job_id);
        } catch (err) {
            toast.error("Failed to start cleaner");
            setIsProcessing(false);
        }
    };

    const reset = () => {
        setFile(null);
        setOriginalUrl(null);
        setResultUrl(null);
        setShowMetrics(false);
        stopPolling();
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] gap-6" onClick={() => { if (showMetrics) setShowMetrics(false); }}>

            {/* Header ... */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/tools" className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                            <span className="text-pink-500 bg-pink-500/10 p-2 rounded-lg"><Eraser className="w-5 h-5" /></span>
                            Bubble Eraser
                        </h1>
                    </div>
                </div>

                {resultUrl && (
                    <div className="flex gap-2 animate-in fade-in slide-in-from-right duration-500">
                        <button onClick={reset} className="px-4 py-2 hover:bg-slate-800 text-slate-300 rounded-lg flex items-center gap-2 font-medium transition-colors">
                            <Sparkles className="w-4 h-4" /> Clean Another
                        </button>
                        <a href={resultUrl} download className="px-5 py-2 bg-pink-600 hover:bg-pink-500 text-white rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-pink-500/20 hover:scale-105 transition-all">
                            <Download className="w-4 h-4" /> Download Clean Image
                        </a>
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden relative flex flex-col items-center justify-center shadow-inner">

                {!file ? (
                    <div className="w-full max-w-xl p-8 animate-in zoom-in-95 duration-500 flex flex-col items-center gap-8">

                        {/* Mode Selector */}
                        <div className="flex bg-slate-800/50 p-1 rounded-xl border border-slate-700/50">
                            <button
                                onClick={() => setCleaningStrategy('clean_text')}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${cleaningStrategy === 'clean_text' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                            >
                                Clean Text (Fill)
                            </button>
                            <button
                                onClick={() => setCleaningStrategy('remove_bubble')}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${cleaningStrategy === 'remove_bubble' ? 'bg-pink-600 text-white shadow-lg shadow-pink-500/20' : 'text-slate-400 hover:text-slate-200'}`}
                            >
                                Magic Erase (LaMa)
                            </button>
                        </div>

                        <SmartDropzone onFileSelect={handleFileSelect} />
                        <p className="text-center text-slate-500 text-sm max-w-sm">
                            {cleaningStrategy === 'clean_text'
                                ? "Removes text inside bubbles and fills with background color."
                                : "Completely removes bubbles and uses AI to hallucinate the background behind them."}
                        </p>
                    </div>
                ) : (
                    <div className="relative w-full h-full flex flex-col">

                        {/* Progress and Notifications Overlay */}
                        <div className="absolute top-6 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center gap-4 w-full max-w-sm pointer-events-none">

                            {/* --- PREMIUM LOADER --- */}
                            {isProcessing && (
                                <div className="bg-slate-900/95 backdrop-blur-xl border border-pink-500/20 px-6 py-5 rounded-2xl flex flex-col gap-3 shadow-2xl pointer-events-auto w-full animate-in zoom-in-95 duration-300">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="relative">
                                                <div className="absolute inset-0 bg-pink-500 blur-md opacity-20 animate-pulse"></div>
                                                <Loader2 className="w-5 h-5 text-pink-400 animate-spin relative z-10" />
                                            </div>
                                            <span className="text-slate-200 font-medium text-sm">
                                                {job?.step?.includes("Removing") ? "Scrubbing Pixels..." :
                                                    "Cleaning Page..."}
                                            </span>
                                        </div>
                                        <span className="text-xs font-bold text-pink-400">{Math.round(job?.progress || 0)}%</span>
                                    </div>

                                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-pink-500 to-purple-500 transition-all duration-500 ease-out shadow-[0_0_10px_rgba(236,72,153,0.5)]"
                                            style={{ width: `${job?.progress || 0}%` }}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* --- RESULT SUMMARY --- */}
                            {!isProcessing && showMetrics && (
                                <div className="animate-in fade-in slide-in-from-top-4 duration-700 bg-slate-900/80 backdrop-blur-md border border-slate-700/50 p-1 rounded-2xl shadow-2xl flex flex-col gap-0 pointer-events-auto min-w-[280px] cursor-pointer" onClick={(e) => { e.stopPropagation(); setShowMetrics(false); }}>

                                    <div className="flex items-center gap-3 px-4 py-3 bg-slate-800/50 rounded-xl">
                                        <div className="p-2 bg-green-500/10 rounded-full text-green-400">
                                            <Sparkles className="w-4 h-4" />
                                        </div>
                                        <div className="flex-1">
                                            <h4 className="text-white font-medium text-sm">Cleaning Complete</h4>
                                            <p className="text-slate-500 text-xs">Bubbles removed successfully</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="h-full w-full p-4 md:p-8">
                            <div className="h-full w-full max-w-5xl mx-auto shadow-2xl rounded-xl overflow-hidden border border-slate-700/50 bg-slate-950/50">
                                <ImageComparator
                                    originalSrc={originalUrl || ""}
                                    cleanedSrc={resultUrl || originalUrl || ""} // Show original until done
                                />
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
