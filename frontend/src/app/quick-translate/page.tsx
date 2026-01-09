"use client";

import { useState, useEffect } from "react";
import PipelineStepper from "@/app/components/translate/PipelineStepper";
import DualPanelView from "@/app/components/translate/DualPanelView";
import SmartDropzone from "@/app/components/upload/SmartDropzone";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function QuickTranslatePage() {
    // Mock State for Demo
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState("idle"); // idle, processing, completed
    const [currentStep, setCurrentStep] = useState("idle");

    // Simulation Loop
    useEffect(() => {
        if (status === 'processing') {
            const sequence = [
                { id: "upload", delay: 1000 },
                { id: "detect", delay: 2500 },
                { id: "ocr", delay: 4000 },
                { id: "translate", delay: 5500 },
                { id: "render", delay: 7000 },
                { id: "completed", delay: 8000 },
            ];

            let timeouts: NodeJS.Timeout[] = [];

            sequence.forEach(({ id, delay }) => {
                const t = setTimeout(() => {
                    setCurrentStep(id);
                    if (id === 'completed') setStatus('completed');
                }, delay);
                timeouts.push(t);
            });

            return () => timeouts.forEach(clearTimeout);
        }
    }, [status]);

    const handleFileSelect = (uploadedFile: File) => {
        setFile(uploadedFile);
        setStatus("processing");
        setCurrentStep("upload");
    };

    const resetPipeline = () => {
        setStatus('idle');
        setFile(null);
        setCurrentStep('idle');
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] gap-6">

            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/" className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <span className="text-indigo-400">⚡</span> Quick Translate Pipeline
                    </h1>
                </div>

                {status === 'completed' && (
                    <button
                        onClick={resetPipeline}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-bold shadow-sm transition-colors"
                    >
                        New Scan
                    </button>
                )}
            </div>

            {/* Main Content Area */}
            {status === 'idle' ? (
                // State: Upload (Empty)
                <div className="flex-1 flex items-center justify-center p-12">
                    <div className="w-full max-w-2xl h-80">
                        <SmartDropzone onFileSelect={handleFileSelect} />
                    </div>
                </div>
            ) : (
                // State: Processing / Result
                <div className="flex-1 flex gap-6 min-h-0 animate-in fade-in zoom-in-95 duration-300">
                    {/* Left: Pipeline Status (Sticky) */}
                    <div className="w-72 shrink-0 bg-slate-900/50 p-6 rounded-xl border border-slate-800/50 backdrop-blur-sm">
                        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6 border-b border-slate-800 pb-2">
                            Pipeline Status
                        </h2>
                        <PipelineStepper currentStepId={currentStep} />
                    </div>

                    {/* Right: Dual View */}
                    <div className="flex-1 min-w-0">
                        <DualPanelView
                            originalSrc={file ? "https://placehold.co/800x1200/222/FFF/png?text=Input" : null}
                            resultSrc={status === 'completed' ? "https://placehold.co/800x1200/222/818cf8/png?text=Translated+Result" : null}
                            isProcessing={status === 'processing'}
                        />
                    </div>
                </div>
            )}

        </div>
    );
}
