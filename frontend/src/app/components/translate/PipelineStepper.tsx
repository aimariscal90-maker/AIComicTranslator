"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

interface Step {
    id: string;
    label: string;
}

interface PipelineStepperProps {
    currentStepId: string;
}

const steps: Step[] = [
    { id: "upload", label: "Uploading Image" },
    { id: "detect", label: "Example: Scanning Bubbles (YOLO)" },
    { id: "ocr", label: "Reading Text (OCR)" },
    { id: "translate", label: "Translating (DeepL)" },
    { id: "render", label: "Rendering Final Page" },
];

export default function PipelineStepper({ currentStepId }: PipelineStepperProps) {
    // Find current step index
    const currentIndex = steps.findIndex(s => s.id === currentStepId);
    // Default to 0 if not started, or max if completed
    const activeIndex = currentIndex === -1 ? (currentStepId === "completed" ? steps.length : 0) : currentIndex;

    return (
        <div className="w-full max-w-xs space-y-4">
            {steps.map((step, index) => {
                const isCompleted = index < activeIndex;
                const isCurrent = index === activeIndex;
                const isPending = index > activeIndex;

                return (
                    <div key={step.id} className="flex items-center gap-3 relative">
                        {/* Connector Line */}
                        {index !== steps.length - 1 && (
                            <div className={`absolute left-2.5 top-7 w-0.5 h-6 -ml-px ${isCompleted ? "bg-emerald-500" : "bg-slate-700"
                                }`} />
                        )}

                        <div className="relative z-10">
                            {isCompleted ? (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="w-5 h-5 bg-black rounded-full text-emerald-500"
                                >
                                    <CheckCircle2 className="w-5 h-5" />
                                </motion.div>
                            ) : isCurrent ? (
                                <div className="w-5 h-5 flex items-center justify-center">
                                    <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                                </div>
                            ) : (
                                <div className="w-5 h-5 text-slate-700">
                                    <Circle className="w-5 h-5" />
                                </div>
                            )}
                        </div>

                        <span className={`text-sm font-medium ${isCompleted ? "text-slate-500" :
                                isCurrent ? "text-indigo-400" : "text-slate-600"
                            }`}>
                            {step.label}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}
