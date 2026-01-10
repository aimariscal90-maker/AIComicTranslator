"use client";

import { useState } from "react";
import SmartDropzone from "@/app/components/upload/SmartDropzone";
import DualPanelView from "@/app/components/translate/DualPanelView";
import { ArrowLeft, Download, Wand2, Loader2, RefreshCw } from "lucide-react";
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

    // Polling logic
    const { startPolling, job, stopPolling } = usePolling({
        onComplete: (completedJob) => {
            setIsProcessing(false);
            if (completedJob.result?.final_url) {
                setResultUrl(getFullUrl(completedJob.result.final_url));
            }
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
        stopPolling();
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] gap-6">

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

                        {/* Premium Toggle */}
                        <div className="mt-8 flex items-center gap-4 bg-slate-800/50 p-4 rounded-xl border border-slate-700 w-full hover:bg-slate-800/80 transition-colors">
                            <div className={`p-3 rounded-full ${isPremium ? 'bg-amber-500/20 text-amber-500' : 'bg-slate-700 text-slate-400'} transition-colors`}>
                                <Wand2 className="w-6 h-6" />
                            </div>
                            <div className="flex-1">
                                <h4 className="text-white font-bold flex items-center gap-2">
                                    Premium Style Cloning Mode
                                    {isPremium && <span className="ml-2 text-[10px] uppercase bg-amber-500 text-slate-900 px-2 py-0.5 rounded-full font-bold">Active</span>}
                                </h4>
                                <p className="text-slate-400 text-sm">
                                    Replicates original fonts, colors, and styles. (Slower)
                                </p>
                            </div>
                            <div
                                onClick={() => setIsPremium(!isPremium)}
                                className={`w-14 h-8 rounded-full p-1 transition-colors duration-300 relative cursor-pointer ${isPremium ? 'bg-amber-500' : 'bg-slate-700'}`}
                            >
                                <div className={`w-6 h-6 bg-white rounded-full shadow-lg transition-transform duration-300 ${isPremium ? 'translate-x-6' : 'translate-x-0'}`} />
                            </div>
                        </div>

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

                        {/* Progress Indicator (Floating) */}
                        {isProcessing && (
                            <div className="absolute top-6 left-1/2 -translate-x-1/2 z-30 bg-slate-950/90 backdrop-blur-md border border-indigo-500/30 px-6 py-3 rounded-full flex items-center gap-4 shadow-2xl">
                                <Loader2 className="w-5 h-5 text-indigo-500 animate-spin" />
                                <div className="flex flex-col">
                                    <span className="text-white font-bold text-sm">{job?.step || "Processing..."}</span>
                                    <div className="h-1 w-32 bg-slate-800 rounded-full mt-1 overflow-hidden">
                                        <div
                                            className="h-full bg-indigo-500 transition-all duration-300 ease-out"
                                            style={{ width: `${job?.progress || 0}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

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
