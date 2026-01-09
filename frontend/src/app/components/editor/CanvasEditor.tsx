"use client";

import { useState } from "react";
import { Move } from "lucide-react";

interface Bubble {
    id: string;
    x: number;
    y: number;
    text: string;
}

export default function CanvasEditor() {
    // Mock Bubbles for demo
    const [bubbles, setBubbles] = useState<Bubble[]>([
        { id: "1", x: 20, y: 15, text: "Wait... what IS that?" },
        { id: "2", x: 60, y: 40, text: "It's the new design system!" },
    ]);

    // Simple drag simulation logic would go here

    return (
        <div className="relative h-full aspect-[2/3] max-w-full bg-white shadow-2xl">
            {/* Background Page */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
                src="https://placehold.co/800x1200/EEE/AAA/png?text=Comic+Page+Cleaning+Complete"
                className="w-full h-full object-contain pointer-events-none"
                alt="Editor Canvas"
            />

            {/* Overlays */}
            {bubbles.map(bubble => (
                <div
                    key={bubble.id}
                    className="absolute bg-white/90 border-2 border-indigo-500 text-slate-900 p-2 rounded min-w-[120px] shadow-lg cursor-grab hover:scale-105 active:cursor-grabbing transition-transform"
                    style={{ left: `${bubble.x}%`, top: `${bubble.y}%` }}
                >
                    <p className="text-center font-comic font-bold text-sm outline-none" contentEditable suppressContentEditableWarning>
                        {bubble.text}
                    </p>

                    <div className="absolute -top-3 -right-3 w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-white cursor-pointer hover:bg-indigo-500 shadow-sm">
                        <Move className="w-3 h-3" />
                    </div>
                </div>
            ))}
        </div>
    );
}
