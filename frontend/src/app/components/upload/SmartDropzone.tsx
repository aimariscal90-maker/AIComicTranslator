"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileImage, X, CheckCircle2 } from "lucide-react";

interface SmartDropzoneProps {
    onFileSelect: (file: File) => void;
}

export default function SmartDropzone({ onFileSelect }: SmartDropzoneProps) {
    const [file, setFile] = useState<File | null>(null);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles?.length > 0) {
            const selected = acceptedFiles[0];
            setFile(selected);
            onFileSelect(selected);
        }
    }, [onFileSelect]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
            'application/pdf': ['.pdf']
        },
        maxFiles: 1
    });

    const clearFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setFile(null);
    };

    return (
        <div className="w-full h-full min-h-[300px]">
            <div
                {...getRootProps()}
                className={`w-full h-full rounded-xl border-2 border-dashed transition-all duration-300 relative overflow-hidden cursor-pointer flex flex-col items-center justify-center p-8
          ${isDragActive
                        ? "border-indigo-500 bg-indigo-500/10 scale-[1.02]"
                        : "border-slate-700 hover:border-slate-500 hover:bg-slate-800/50 bg-slate-900/50"
                    }
        `}
            >
                <input {...getInputProps()} />

                <AnimatePresence mode="wait">
                    {file ? (
                        <motion.div
                            key="file"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex flex-col items-center text-center"
                        >
                            <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-500 mb-4">
                                <CheckCircle2 className="w-8 h-8" />
                            </div>
                            <p className="text-white font-medium text-lg truncate max-w-xs">{file.name}</p>
                            <p className="text-slate-400 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>

                            <button
                                onClick={clearFile}
                                className="mt-6 px-4 py-2 bg-slate-800 hover:bg-red-500/10 hover:text-red-400 text-slate-300 rounded-lg text-sm transition-colors flex items-center gap-2"
                            >
                                <X className="w-4 h-4" /> Change File
                            </button>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="empty"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-col items-center text-center space-y-4"
                        >
                            <div className={`p-4 rounded-full transition-colors ${isDragActive ? "bg-indigo-500 text-white" : "bg-slate-800 text-slate-400"}`}>
                                <UploadCloud className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-lg font-bold text-white">
                                    {isDragActive ? "Drop it here!" : "Drag & Drop your comic page"}
                                </p>
                                <p className="text-sm text-slate-400 mt-1">
                                    Supports JPG, PNG, WEBP, PDF
                                </p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Decorative Grid Background */}
                <div className="absolute inset-0 z-[-1] opacity-[0.03]"
                    style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }}
                />
            </div>
        </div>
    );
}
