"use client";

import { useState } from "react";
import SmartDropzone from "@/app/components/upload/SmartDropzone";
import DualPanelView from "@/app/components/translate/DualPanelView";
import { ArrowLeft, Download, Wand2, Loader2, RefreshCw, Clock } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import api from "@/services/api";
import { usePolling } from "@/hooks/usePolling";
import { API_URL } from "@/config";

export default function TranslatorToolPage() {
    const [file, setFile] = useState<File | null>(null);
    const [originalUrl, setOriginalUrl] = useState<string | null>(null);
    const [resultUrl, setResultUrl] = useState<string | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isPremium, setIsPremium] = useState(false); // New state for Premium Mode

    const [showMetrics, setShowMetrics] = useState(false);

    // Polling logic
    const { startPolling, job, stopPolling } = usePolling({
        onComplete: (completedJob) => {
            setIsProcessing(false);
            if (completedJob.result?.final_url) {
                setResultUrl(getFullUrl(completedJob.result.final_url));
            }
            setShowMetrics(true); // Show metrics on completion
            toast.success("Translation Complete!");
        },
        onFail: (err) => {
            setIsProcessing(false);
            toast.error("Translation Failed", { description: err });
        }
    });

    const getFullUrl = (path: string) => {
        if (path.startsWith('http')) return path;
        const cleanPath = path.startsWith('/') ? path.substring(1) : path;
        return `${API_URL}/${cleanPath}`;
    };

    const handleFileSelect = async (uploadedFile: File) => {
        setFile(uploadedFile);
        setOriginalUrl(URL.createObjectURL(uploadedFile));
        setResultUrl(null);
        setIsProcessing(true);

        const formData = new FormData();
        formData.append('file', uploadedFile);
        formData.append('mode', isPremium ? 'premium' : 'full'); // Use state

        try {
            toast.message("Uploading...", { description: "Sending to translation engine." });
            const { data } = await api.post<{ job_id: string }>('/process', formData);
            startPolling(data.job_id); // Start tracking
        } catch (err) {
            toast.error("Failed to start translation");
            setIsProcessing(false);
            setFile(null);
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

            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/tools" className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                            <span className="text-indigo-500 bg-indigo-500/10 p-2 rounded-lg"><Wand2 className="w-5 h-5" /></span>
                            Image Translator
                        </h1>
                    </div>
                </div>

                {resultUrl && (
                    <div className="flex gap-2 animate-in fade-in slide-in-from-right duration-500">
                        <button onClick={reset} className="px-4 py-2 hover:bg-slate-800 text-slate-300 rounded-lg flex items-center gap-2 font-medium transition-colors">
                            <RefreshCw className="w-4 h-4" /> Translate Another
                        </button>
                        <a href={resultUrl} download className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all hover:scale-105">
                            <Download className="w-4 h-4" /> Download Result
                        </a>
                    </div>
                )}
            </div>

            {/* Main Content Area */}
            <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden relative flex flex-col items-center justify-center shadow-inner">

                {/* Initial State: Dropzone */}
                {!file ? (
                    <div className="w-full max-w-xl p-8 animate-in zoom-in-95 duration-500 flex flex-col items-center">
                        <SmartDropzone onFileSelect={handleFileSelect} />



                        <div className="text-center mt-6 space-y-2">
                            <h3 className="text-white font-bold text-lg">AI-Powered Comic Translation</h3>
                            <p className="text-slate-500 text-sm max-w-sm mx-auto">
                                Automatically detects bubbles, removes text, translates, and re-renders in Spanish.
                            </p>
                        </div>
                    </div>
                ) : (
                    // Processing / Result State
                    <div className="relative w-full h-full flex flex-col">

                        {/* Progress and Timings */}
                        <div className="absolute top-6 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center gap-4 w-full max-w-sm pointer-events-none">

                            {/* --- PREMIUM LOADER --- */}
                            {isProcessing && (
                                <div className="bg-slate-900/95 backdrop-blur-xl border border-indigo-500/20 px-6 py-5 rounded-2xl flex flex-col gap-3 shadow-2xl pointer-events-auto w-full animate-in zoom-in-95 duration-300">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="relative">
                                                <div className="absolute inset-0 bg-indigo-500 blur-md opacity-20 animate-pulse"></div>
                                                <Loader2 className="w-5 h-5 text-indigo-400 animate-spin relative z-10" />
                                            </div>
                                            <span className="text-slate-200 font-medium text-sm">
                                                {/* Map technical steps to friendly names */}
                                                {job?.step?.includes("Extracting") ? "Analyzing Page..." :
                                                    job?.step?.includes("OCR") ? "Reading Text..." :
                                                        job?.step?.includes("Translation") ? "Translating Story..." :
                                                            job?.step?.includes("Removing") ? "Cleaning Artwork..." :
                                                                job?.step?.includes("Rendering") ? "Typesetting..." :
                                                                    job?.step || "Working Magic..."}
                                            </span>
                                        </div>
                                        <span className="text-xs font-bold text-indigo-400">{Math.round(job?.progress || 0)}%</span>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 ease-out shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                                            style={{ width: `${job?.progress || 0}%` }}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* --- RESULT SUMMARY (Friendly) --- */}
                            {!isProcessing && job?.result?.timings && showMetrics && (
                                <div className="animate-in fade-in slide-in-from-top-4 duration-700 bg-slate-900/80 backdrop-blur-md border border-slate-700/50 p-1 rounded-2xl shadow-2xl flex flex-col gap-0 pointer-events-auto min-w-[280px] cursor-pointer" onClick={(e) => { e.stopPropagation(); setShowMetrics(false); }}>

                                    {/* Header Badge */}
                                    <div className="flex items-center gap-3 px-4 py-3 bg-slate-800/50 rounded-xl">
                                        <div className="p-2 bg-green-500/10 rounded-full text-green-400">
                                            <Clock className="w-4 h-4" />
                                        </div>
                                        <div className="flex-1">
                                            <h4 className="text-white font-medium text-sm">Translation Complete</h4>
                                            <p className="text-slate-500 text-xs">Ready for download</p>
                                        </div>
                                        <div className="text-right">
                                            <span className="block text-lg font-bold text-white tracking-tight">{job.result.timings.total_time}s</span>
                                            <span className="text-[10px] uppercase text-slate-500 font-bold tracking-wider">Total Time</span>
                                        </div>
                                    </div>

                                    {/* Simple Breakdown (Horizontal) */}
                                    <div className="grid grid-cols-3 divide-x divide-slate-700/50 p-2 text-center mt-1">
                                        <div className="px-2 py-1">
                                            <span className="block text-[10px] text-slate-500 uppercase font-bold text-xs">Read</span>
                                            <span className="text-xs text-slate-300 font-medium">{job.result.timings.ocr_processing}s</span>
                                        </div>
                                        <div className="px-2 py-1">
                                            <span className="block text-[10px] text-slate-500 uppercase font-bold text-xs">Clean</span>
                                            <span className="text-xs text-slate-300 font-medium">{job.result.timings.inpainting}s</span>
                                        </div>
                                        <div className="px-2 py-1">
                                            <span className="block text-[10px] text-slate-500 uppercase font-bold text-xs">Typeset</span>
                                            <span className="text-xs text-slate-300 font-medium">{job.result.timings.text_rendering}s</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Visualizer */}
                        <div className="flex-1 p-4 md:p-8">
                            <div className="h-full w-full mx-auto shadow-2xl rounded-xl overflow-hidden border border-slate-700/50 bg-slate-950/50">
                                {/* We reuse DualPanelView for the nice side-by-side or slider effect */}
                                {/* But we want it to look like a tool result */}
                                <DualPanelView
                                    originalSrc={originalUrl || ""}
                                    resultSrc={resultUrl}
                                    isProcessing={isProcessing}
                                />
                            </div>
                        </div>

                    </div>
                )}

            </div>
        </div>
    );
}
