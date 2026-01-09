"use client";

import { usePathname } from "next/navigation";
import { Bell, Search } from "lucide-react";

export default function TopNav() {
    const pathname = usePathname();
    const pathSegments = pathname.split('/').filter(Boolean);

    return (
        <header className="fixed top-0 left-64 right-0 h-16 bg-slate-950/80 backdrop-blur-md border-b border-slate-900 flex items-center justify-between px-8 z-40">
            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 text-sm text-slate-500">
                <span className="hover:text-slate-300 cursor-pointer transition-colors">ComicOS</span>
                {pathSegments.map((segment, index) => (
                    <div key={index} className="flex items-center gap-2">
                        <span>/</span>
                        <span className="capitalize text-slate-200 font-medium">
                            {segment.replace('-', ' ')}
                        </span>
                    </div>
                ))}
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
                {/* System Status */}
                <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 rounded-full border border-slate-800">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    <span className="text-xs font-medium text-slate-400">System Online</span>
                </div>

                <div className="w-px h-6 bg-slate-800" />

                <button className="text-slate-400 hover:text-white transition-colors">
                    <Search className="w-5 h-5" />
                </button>
                <button className="text-slate-400 hover:text-white transition-colors relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border-2 border-slate-950" />
                </button>
            </div>
        </header>
    );
}
