"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FlaskConical, Loader2, CheckCircle, Search, RefreshCw, Eye } from "lucide-react";
import Image from "next/image";

// Endpoint: POST /analyze-style (FormData: file)

export default function LabPage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<any>(null);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const f = e.target.files[0];
            setFile(f);
            const url = URL.createObjectURL(f);
            setPreview(url);
            setResult(null);
        }
    };

    const runAnalysis = async () => {
        if (!file) return;

        setIsAnalyzing(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/analyze-style", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Analysis failed");

            const data = await res.json();
            setResult(data);
        } catch (error) {
            console.error(error);
            alert("Error running analysis. Is backend running?");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8 pb-20">
            {/* Header */}
            <div className="flex items-center gap-4 py-8 border-b border-slate-800">
                <div className="bg-indigo-500/10 p-4 rounded-2xl">
                    <FlaskConical className="w-10 h-10 text-indigo-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">Style Lab (Phase 1)</h1>
                    <p className="text-slate-400">
                        Upload a cropped text bubble to verify <b>Binarization</b> & <b>Contour Detection</b>.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left: Input */}
                <div className="space-y-6">
                    <div className="bg-slate-900 border-2 border-dashed border-slate-800 rounded-3xl p-10 flex flex-col items-center justify-center text-center hover:bg-slate-800/50 transition-colors relative min-h-[300px]">

                        <input
                            type="file"
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                            accept="image/*"
                            onChange={handleFileSelect}
                        />

                        {preview ? (
                            <div className="relative w-full h-full flex items-center justify-center">
                                <Image
                                    src={preview}
                                    alt="Preview"
                                    width={400}
                                    height={300}
                                    className="max-h-[300px] w-auto object-contain rounded-lg shadow-2xl"
                                />
                                <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity">
                                    <p className="text-white font-medium">Click to change</p>
                                </div>
                            </div>
                        ) : (
                            <>
                                <Upload className="w-16 h-16 text-slate-600 mb-6" />
                                <h3 className="text-xl font-bold text-slate-300 mb-2">Upload Test Image</h3>
                                <p className="text-slate-500 max-w-xs">
                                    Drop a cropped text image here to analyze pixels.
                                </p>
                            </>
                        )}
                    </div>

                    <button
                        onClick={runAnalysis}
                        disabled={!file || isAnalyzing}
                        className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all ${!file
                                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                                : isAnalyzing
                                    ? "bg-indigo-500/50 text-indigo-200 cursor-wait"
                                    : "bg-indigo-500 hover:bg-indigo-400 text-white shadow-lg shadow-indigo-500/20 hover:scale-[1.02]"
                            }`}
                    >
                        {isAnalyzing ? (
                            <><Loader2 className="w-6 h-6 animate-spin" /> Analyzing...</>
                        ) : (
                            <><FlaskConical className="w-6 h-6" /> Run Pixel Analysis</>
                        )}
                    </button>

                    {/* Instructions */}
                    <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-6">
                        <h4 className="flex items-center gap-2 font-bold text-amber-400 mb-2">
                            <Eye className="w-5 h-5" /> What to look for:
                        </h4>
                        <ul className="list-disc list-inside text-sm text-slate-400 space-y-1 ml-1">
                            <li><b>Binary Mask:</b> Should be pure black/white using Otsu. Text should be white (255).</li>
                            <li><b>Contours:</b> Red lines should outline every letter perfectly.</li>
                            <li><b>Data:</b> Check if `density` and `estimated_font_size` make sense.</li>
                        </ul>
                    </div>
                </div>

                {/* Right: Results */}
                <div className="space-y-6">
                    {!result ? (
                        <div className="h-full min-h-[400px] bg-slate-900/50 rounded-3xl border border-slate-800 flex items-center justify-center text-slate-600">
                            Waiting for analysis...
                        </div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-6"
                        >
                            {/* Visual Debug */}
                            <div className="grid grid-cols-2 gap-4">
                                <DebugCard title="Binary Mask (Otsu)" src={`http://localhost:8000${result.mask_url}`} />
                                <DebugCard title="Contours (Letters)" src={`http://localhost:8000${result.contours_url}`} />
                            </div>

                            {/* Data Panel */}
                            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                    <Search className="w-5 h-5 text-indigo-400" />
                                    Analysis Data (JSON)
                                </h3>
                                <pre className="bg-black/50 p-4 rounded-xl text-xs text-indigo-300 font-mono overflow-auto max-h-[300px] border border-slate-800">
                                    {JSON.stringify(result.style, null, 2)}
                                </pre>

                                <div className="grid grid-cols-2 gap-4">
                                    <Metric label="Font Size" value={`${result.style.estimated_font_size}px`} />
                                    <Metric label="Is Bold?" value={result.style.is_bold ? "YES" : "NO"} active={result.style.is_bold} />
                                    <Metric label="Density" value={result.style.density.toFixed(3)} />
                                    <Metric label="Format" value={result.style.is_inverted ? "Inverted (White)" : "Standard (Black)"} />
                                </div>
                            </div>
                        </motion.div>
                    )}
                </div>
            </div>
        </div>
    );
}

function DebugCard({ title, src }: { title: string, src: string }) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden group">
            <div className="relative aspect-video bg-black/50">
                <Image
                    src={src}
                    alt={title}
                    fill
                    className="object-contain"
                    unoptimized // Important for local backend images
                />
            </div>
            <div className="p-3 border-t border-slate-800 bg-slate-900">
                <p className="text-sm font-bold text-slate-300 text-center">{title}</p>
            </div>
        </div>
    );
}

function Metric({ label, value, active = false }: { label: string, value: string | number, active?: boolean }) {
    return (
        <div className={`p-3 rounded-xl border ${active ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-slate-800/50 border-slate-700'}`}>
            <p className="text-xs text-slate-500 uppercase font-bold">{label}</p>
            <p className={`text-lg font-mono font-bold ${active ? 'text-emerald-400' : 'text-slate-200'}`}>{value}</p>
        </div>
    );
}
