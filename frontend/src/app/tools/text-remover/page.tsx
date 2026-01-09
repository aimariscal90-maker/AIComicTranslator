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

    const { startPolling, job, stopPolling } = usePolling({
        onComplete: (completedJob) => {
            setIsProcessing(false);
            if (completedJob.result?.final_url) {
                setResultUrl(getFullUrl(completedJob.result.final_url));
            }
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

    const handleFileSelect = async (uploadedFile: File) => {
        setFile(uploadedFile);
        setOriginalUrl(URL.createObjectURL(uploadedFile));
        setResultUrl(null);
        setIsProcessing(true);

        const formData = new FormData();
        formData.append('file', uploadedFile);
        formData.append('mode', 'clean_only'); // Enable Cleaner Mode

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
                            <span className="text-pink-500 bg-pink-500/10 p-2 rounded-lg"><Eraser className="w-5 h-5" /></span>
                            Bubble Eraser
                        </h1>
                    </div>
                </div>

                {resultUrl && (
                    <div className="flex gap-2">
                        <button onClick={reset} className="px-4 py-2 hover:bg-slate-800 text-slate-300 rounded-lg">
                            Clean Another
                        </button>
                        <a href={resultUrl} download className="px-4 py-2 bg-pink-600 hover:bg-pink-500 text-white rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-pink-500/20">
                            <Download className="w-4 h-4" /> Download Clean Image
                        </a>
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden relative flex flex-col items-center justify-center">

                {!file ? (
                    <div className="w-full max-w-xl p-8">
                        <SmartDropzone onFileSelect={handleFileSelect} />
                        <p className="text-center text-slate-500 mt-4 text-sm">
                            Upload a page. AI will remove all text bubbles automatically.
                        </p>
                    </div>
                ) : (
                    <div className="relative w-full h-full p-4">
                        {isProcessing && (
                            <div className="absolute inset-0 z-20 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center">
                                <Loader2 className="w-12 h-12 text-pink-500 animate-spin mb-4" />
                                <h3 className="text-xl font-bold text-white">Scrubbing Pixels...</h3>
                                <p className="text-slate-400">{job?.step || "Initializing..."}</p>
                            </div>
                        )}

                        <div className="h-full w-full max-w-4xl mx-auto shadow-2xl rounded-lg overflow-hidden border border-slate-700">
                            <ImageComparator
                                originalSrc={originalUrl || ""}
                                cleanedSrc={resultUrl || originalUrl || ""} // Show original until done
                            />
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
