"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FlaskConical, Loader2, CheckCircle, Search, RefreshCw, Eye, Layout, Type, Palette } from "lucide-react";
import Image from "next/image";

// TABS: 'pixel' (Original Lab) | 'pipeline' (New Premium Debug)

export default function LabPage() {
    const [activeTab, setActiveTab] = useState<'pixel' | 'pipeline'>('pipeline'); // Default to new one
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<any>(null); // Shared result state (structure differs per tab)
    const [pipelinePreview, setPipelinePreview] = useState<string | null>(null);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const f = e.target.files[0];
            setFile(f);
            const url = URL.createObjectURL(f);
            setPreview(url);
            setResult(null);
            setPipelinePreview(null);
        }
    };

    const runAnalysis = async () => {
        if (!file) return;
        setIsAnalyzing(true);
        setPipelinePreview(null);
        const formData = new FormData();
        formData.append("file", file);

        // Different endpoint based on tab
        const endpoint = activeTab === 'pixel'
            ? "http://localhost:8000/analyze-style"
            : "http://localhost:8000/debug-pipeline";

        try {
            const res = await fetch(endpoint, { method: "POST", body: formData });
            if (!res.ok) throw new Error("Analysis failed");
            const data = await res.json();

            if (activeTab === 'pipeline' && !Array.isArray(data)) {
                // New Object Response
                setResult({ ...data, bubbles: data.bubbles });
                setPipelinePreview(data.preview_url);
            } else {
                setResult(data);
            }
        } catch (error) {
            console.error(error);
            alert("Error running analysis. Is backend running?");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8 pb-20 px-4">
            {/* Header with Tabs */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 py-8 border-b border-slate-800">
                <div className="flex items-center gap-4">
                    <div className="bg-indigo-500/10 p-4 rounded-2xl">
                        <FlaskConical className="w-10 h-10 text-indigo-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Engineering Lab</h1>
                        <p className="text-slate-400">Debug & Validate AI Pipeline Steps</p>
                    </div>
                </div>

                <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800">
                    <TabButton active={activeTab === 'pipeline'} onClick={() => { setActiveTab('pipeline'); setResult(null); }} label="Pipeline Debug" icon={<Layout className="w-4 h-4" />} />
                    <TabButton active={activeTab === 'pixel'} onClick={() => { setActiveTab('pixel'); setResult(null); }} label="Pixel Microscope" icon={<Search className="w-4 h-4" />} />
                </div>
            </div>

            {/* Input Section (Shared) */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 flex flex-col md:flex-row gap-8 items-center">
                <div className="relative group cursor-pointer">
                    <input type="file" onChange={handleFileSelect} className="absolute inset-0 z-10 opacity-0 cursor-pointer" accept="image/*" />
                    <div className={`w-64 h-40 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center gap-2 transition-all ${file ? 'border-indigo-500/50 bg-indigo-500/10' : 'border-slate-700 hover:border-slate-500'}`}>
                        {file ? <CheckCircle className="w-8 h-8 text-indigo-400" /> : <Upload className="w-8 h-8 text-slate-500" />}
                        <p className="text-sm font-medium text-slate-400">{file ? file.name : "Upload Image"}</p>
                    </div>
                </div>

                <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2">
                        {activeTab === 'pipeline' ? "Full Page Analysis" : "Single Crop Analysis"}
                    </h3>
                    <p className="text-slate-400 mb-6 max-w-lg">
                        {activeTab === 'pipeline'
                            ? "Simulate the full Premium Pipeline: Detects bubbles, runs Google OCR on each, extracts generic style, and matches fonts."
                            : "Analyze a single cropped bubble image to see the raw pixel data (Binary Mask, Contours) used for stylometry."}
                    </p>

                    <button
                        onClick={runAnalysis}
                        disabled={!file || isAnalyzing}
                        className={`px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all ${!file ? 'bg-slate-800 text-slate-600' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'}`}
                    >
                        {isAnalyzing ? <><Loader2 className="w-5 h-5 animate-spin" /> Running...</> : <><FlaskConical className="w-5 h-5" /> Run Test</>}
                    </button>
                </div>
            </div>

            {/* Results Area */}
            {result && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">

                    {activeTab === 'pixel' ? (
                        // PIXEL LAB VIEW (Old View)
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <h3 className="text-lg font-bold text-slate-300">Visual Layers</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <DebugCard title="Binary Mask" src={`http://localhost:8000${result.mask_url}`} />
                                    <DebugCard title="Contours" src={`http://localhost:8000${result.contours_url}`} />
                                </div>
                            </div>
                            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                                <h3 className="text-lg font-bold text-white mb-4">Stylometry Data</h3>
                                <pre className="bg-black p-4 rounded-xl text-xs text-green-400 font-mono overflow-auto max-h-[400px]">
                                    {JSON.stringify(result.style, null, 2)}
                                </pre>
                            </div>
                        </div>
                    ) : (
                        // PIPELINE LAB VIEW (New View)
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Left: Annotated Page */}
                            <div className="lg:col-span-1 space-y-4">
                                <h3 className="font-bold text-slate-300 flex items-center gap-2"><Eye className="w-4 h-4" /> Step 1: Detection</h3>
                                <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-black">
                                    <Image
                                        src={`http://localhost:8000${result.annotated_url}`}
                                        alt="Detection"
                                        width={600}
                                        height={800}
                                        className="w-full h-auto"
                                        unoptimized
                                    />
                                </div>
                            </div>

                            {/* Right: Bubble List */}
                            <div className="lg:col-span-2 space-y-4">
                                <h3 className="font-bold text-slate-300 flex items-center gap-2"><Type className="w-4 h-4" /> Step 2: OCR & Style Analysis</h3>
                                <div className="space-y-4">
                                    {result.bubbles.map((b: any, idx: number) => (
                                        <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex gap-6 hover:border-indigo-500/50 transition-colors">
                                            {/* Crop Images (RGB + X-Ray) */}
                                            <div className="flex flex-col gap-2 shrink-0">
                                                <div className="w-24 h-20 bg-slate-950 rounded-lg overflow-hidden border border-slate-800 relative">
                                                    {b.crop_url && <Image src={`http://localhost:8000${b.crop_url}`} alt="Crop" fill className="object-contain" unoptimized />}
                                                    <div className="absolute top-1 left-1 bg-black/60 backdrop-blur text-[10px] font-bold text-white px-1.5 py-0.5 rounded">RGB</div>
                                                </div>
                                                <div className="w-24 h-20 bg-slate-950 rounded-lg overflow-hidden border border-slate-800 relative">
                                                    {b.mask_url && <Image src={`http://localhost:8000${b.mask_url}`} alt="Mask" fill className="object-contain" unoptimized />}
                                                    <div className="absolute top-1 left-1 bg-black/60 backdrop-blur text-[10px] font-bold text-emerald-400 px-1.5 py-0.5 rounded">X-RAY</div>
                                                </div>
                                                <p className="text-[10px] text-slate-500 text-center font-mono">#{idx + 1}</p>
                                            </div>

                                            {/* Data */}
                                            <div className="flex-1 grid grid-cols-3 gap-4">
                                                <div>
                                                    <p className="text-xs text-slate-500 uppercase font-bold mb-1">OCR Text</p>
                                                    <p className="text-slate-300 font-mono text-sm bg-black/30 p-2 rounded border border-slate-800 min-h-[40px] break-words">
                                                        {b.ocr_text || <span className="text-red-500 italic">No text</span>}
                                                    </p>
                                                </div>

                                                <div>
                                                    <div className="flex justify-between items-center mb-1">
                                                        <p className="text-xs text-emerald-500 uppercase font-bold">Translation</p>
                                                        <span className="text-[10px] text-emerald-400/70 bg-emerald-950/50 px-1 rounded border border-emerald-900/50">
                                                            {b.trans_provider || 'Pending'}
                                                        </span>
                                                    </div>
                                                    <p className="text-white font-mono text-sm bg-emerald-900/10 p-2 rounded border border-emerald-900/30 min-h-[40px] break-words">
                                                        {b.translation || <span className="text-slate-600 italic">...</span>}
                                                    </p>
                                                </div>

                                                <div>
                                                    <p className="text-xs text-slate-500 uppercase font-bold mb-1">Font Match</p>
                                                    <p className="text-indigo-300 font-bold flex items-center gap-2">
                                                        {b.font_match}
                                                        <span className="text-[10px] bg-indigo-500/20 px-2 py-0.5 rounded text-indigo-200 border border-indigo-500/30">
                                                            {(b.bubble_type || 'speech').toUpperCase()}
                                                        </span>
                                                    </p>
                                                </div>

                                                <div className="col-span-3 grid grid-cols-5 gap-2 pt-2 border-t border-slate-800/50">
                                                    <MiniMetric label="Color" value={b.style.text_color} color={b.style.text_color} />
                                                    <MiniMetric label="Bg" value={b.style.bg_color} color={b.style.bg_color} />
                                                    <MiniMetric label="Size" value={`${b.style.font_size_pt}pt`} />
                                                    <MiniMetric label="Stroke" value={b.style.has_stroke ? "YES" : "NO"} highlight={b.style.has_stroke} />
                                                    <MiniMetric label="Bold" value={b.style.is_bold ? "YES" : "NO"} highlight={b.style.is_bold} />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Step 3: Render Preview (Full Page) */}
                            {pipelinePreview && (
                                <div className="lg:col-span-3 mt-8 border-t border-slate-800 pt-8">
                                    <h3 className="font-bold text-slate-300 flex items-center gap-2 mb-4">
                                        <Palette className="w-4 h-4 text-emerald-400" />
                                        Step 3: Render Verification (Inpainting + Style Cloning)
                                    </h3>
                                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                                        <Image
                                            src={`http://localhost:8000${pipelinePreview}`}
                                            alt="Preview"
                                            width={1200}
                                            height={1600}
                                            className="w-full h-auto rounded-xl shadow-2xl"
                                            unoptimized
                                        />
                                        <p className="mt-4 text-center text-xs text-slate-500">
                                            *Visual Proof: The original text is erased (Inpainting) and re-written using the cloned font/style logic.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                </motion.div>
            )}
        </div>
    );
}

function TabButton({ active, label, icon, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${active ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
        >
            {icon} {label}
        </button>
    );
}

function DebugCard({ title, src }: { title: string, src: string }) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="relative aspect-video bg-black/50">
                <Image src={src} alt={title} fill className="object-contain" unoptimized />
            </div>
            <div className="p-2 bg-slate-950 text-center">
                <p className="text-xs font-bold text-slate-400">{title}</p>
            </div>
        </div>
    );
}

function MiniMetric({ label, value, color, highlight }: any) {
    return (
        <div className={`p-2 rounded bg-slate-950 border border-slate-800 ${highlight ? 'border-emerald-500/50 bg-emerald-500/10' : ''}`}>
            <p className="text-[10px] text-slate-500 uppercase">{label}</p>
            <div className="flex items-center gap-2">
                {color && <div className="w-3 h-3 rounded-full border border-white/20" style={{ background: color }} />}
                <p className={`text-xs font-mono font-bold truncate ${highlight ? 'text-emerald-400' : 'text-slate-300'}`}>{value}</p>
            </div>
        </div>
    );
}
