"use client";

import { useState, useRef, useEffect } from "react";
import { Bubble } from "@/types/api";
import { Move, Save, Loader2, Type } from "lucide-react";
import api from "@/services/api";
import { toast } from "sonner";
import { API_URL } from "@/config";

interface CanvasEditorProps {
    imageUrl: string;
    originalBubbles: Bubble[];
    filename: string;
}

export default function CanvasEditor({ imageUrl, originalBubbles, filename }: CanvasEditorProps) {
    const [bubbles, setBubbles] = useState<Bubble[]>(originalBubbles);
    const [selectedBubbleIndex, setSelectedBubbleIndex] = useState<number | null>(null);
    const [isUpdating, setIsUpdating] = useState(false);
    const [currentImage, setCurrentImage] = useState(imageUrl);
    const [editValue, setEditValue] = useState("");

    // Canvas ref to calculate scaling
    const containerRef = useRef<HTMLDivElement>(null);
    const imgRef = useRef<HTMLImageElement>(null);
    const [scale, setScale] = useState({ x: 1, y: 1 });

    // Update scale on load/resize
    const updateScale = () => {
        if (imgRef.current && imgRef.current.naturalWidth) {
            const renderW = imgRef.current.clientWidth;
            const renderH = imgRef.current.clientHeight;
            const naturalW = imgRef.current.naturalWidth;
            const naturalH = imgRef.current.naturalHeight;
            setScale({
                x: renderW / naturalW,
                y: renderH / naturalH
            });
        }
    };

    useEffect(() => {
        window.addEventListener('resize', updateScale);
        return () => window.removeEventListener('resize', updateScale);
    }, []);

    const handleBubbleClick = (index: number) => {
        setSelectedBubbleIndex(index);
        setEditValue(bubbles[index].translated_text || "");
    };

    const handleSave = async () => {
        if (selectedBubbleIndex === null) return;

        setIsUpdating(true);
        const toastId = toast.loading("Regenerating Image...");

        try {
            const payload = {
                bubble_index: selectedBubbleIndex,
                new_text: editValue,
                font: bubbles[selectedBubbleIndex].font || "ComicNeue"
            };

            // PATCH request to update text
            const { data } = await api.patch(`/process/${filename}/update-bubble`, payload);

            // Update local state
            const updatedBubbles = [...bubbles];
            updatedBubbles[selectedBubbleIndex].translated_text = editValue;
            setBubbles(updatedBubbles);

            // Force image reload with timestamp to bust cache
            setCurrentImage(`${API_URL}${data.final_url}?t=${Date.now()}`);

            toast.success("Text updated!", { id: toastId });
            setSelectedBubbleIndex(null); // Close editor
        } catch (err) {
            console.error(err);
            toast.error("Failed to update text", { id: toastId });
        } finally {
            setIsUpdating(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-100 rounded-lg overflow-hidden">
            <div className="flex-1 relative overflow-hidden flex items-center justify-center bg-slate-900" ref={containerRef}>

                {/* Main Image */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                    ref={imgRef}
                    src={currentImage}
                    onLoad={updateScale}
                    className="max-w-full max-h-full object-contain pointer-events-none select-none"
                    alt="Editor Canvas"
                />

                {/* Bubble Overlays */}
                {bubbles.map((bubble, index) => {
                    // Calculate position based on bbox [x1, y1, x2, y2]
                    const width = (bubble.bbox[2] - bubble.bbox[0]) * scale.x;
                    const height = (bubble.bbox[3] - bubble.bbox[1]) * scale.y;

                    // We need to position relative to the image, which is centered. 
                    // This is tricky with Flexbox centering.
                    // Easier hack: Position overlays relative to the IMG itself if possible, 
                    // OR use a wrapper that matches image dimensions exactly.
                    // For now, let's try a best-effort absolute positioning on top of the container
                    // actually, the best way: The container logic is hard without exact dimensions.
                    // Let's assume standard "object-contain" behavior.

                    return null; // See implementation note below
                })}

                {/* 
                    Better Approach for Overlays: 
                    Wrap img and overlays in a div that is strictly sized to the image aspect ratio.
                 */}
                {imgRef.current && (
                    <div
                        className="absolute"
                        style={{
                            width: imgRef.current.clientWidth,
                            height: imgRef.current.clientHeight
                        }}
                    >
                        {bubbles.map((bubble, index) => {
                            const x = bubble.bbox[0] * scale.x;
                            const y = bubble.bbox[1] * scale.y;
                            const w = (bubble.bbox[2] - bubble.bbox[0]) * scale.x;
                            const h = (bubble.bbox[3] - bubble.bbox[1]) * scale.y;

                            const isSelected = selectedBubbleIndex === index;

                            return (
                                <div
                                    key={index}
                                    onClick={() => handleBubbleClick(index)}
                                    className={`absolute cursor-pointer border-2 transition-all hover:bg-indigo-500/20 group
                                        ${isSelected ? 'border-indigo-500 bg-indigo-500/10 z-20' : 'border-transparent hover:border-indigo-300 z-10'}
                                    `}
                                    style={{
                                        left: x,
                                        top: y,
                                        width: w,
                                        height: h
                                    }}
                                >
                                    {isSelected && (
                                        <div className="absolute -top-8 left-0 bg-indigo-600 text-white text-xs px-2 py-1 rounded shadow flex items-center gap-1">
                                            <Type className="w-3 h-3" /> Editing...
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}

                {isUpdating && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
                        <div className="bg-white p-4 rounded-xl shadow-2xl flex flex-col items-center gap-2">
                            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                            <span className="text-slate-900 font-bold">Rendering Text...</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Editor Bar */}
            <div className="bg-white border-t border-slate-200 p-4 shrink-0 h-24 flex items-center gap-4">
                {selectedBubbleIndex !== null ? (
                    <div className="flex-1 flex gap-4 max-w-3xl mx-auto w-full animate-in slide-in-from-bottom duration-300">
                        <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
                            autoFocus
                            className="flex-1 border text-slate-800 border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none font-comic text-lg"
                            placeholder="Type translation here..."
                        />

                        <button
                            onClick={handleSave}
                            disabled={isUpdating}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Save className="w-4 h-4" /> Save
                        </button>
                    </div>
                ) : (
                    <div className="flex-1 text-center text-slate-400 text-sm">
                        Click on any text bubble in the image to edit its content.
                    </div>
                )}
            </div>
        </div>
    );
}
