"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
    LayoutGrid,
    Sparkles,
    Zap,
    GalleryVerticalEnd,
    Settings,
    LogOut,
    FlaskConical,
    Wrench
} from "lucide-react";
import { cn } from "@/lib/utils";

const menuItems = [
    { icon: LayoutGrid, label: "Dashboard", href: "/" },
    { icon: Zap, label: "Quick Translate", href: "/quick-translate" },
    { icon: Sparkles, label: "Magic Cleaner", href: "/cleaner" },
    { icon: GalleryVerticalEnd, label: "Projects", href: "/projects" },
    { icon: Wrench, label: "Tools", href: "/tools" },
    { icon: FlaskConical, label: "Lab (Tests)", href: "/tests" },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-950 border-r border-slate-900 text-slate-400 flex flex-col z-50">
            {/* Brand */}
            <div className="p-6">
                <div className="flex items-center gap-2 text-white font-bold text-xl tracking-tight">
                    <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <span className="text-lg">⌘</span>
                    </div>
                    <span>Comic<span className="text-indigo-400">OS</span></span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-1">
                <p className="px-4 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 mt-4">
                    Core Modules
                </p>
                {menuItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all group relative",
                                isActive
                                    ? "text-white bg-slate-900"
                                    : "hover:text-slate-200 hover:bg-slate-900/50"
                            )}
                        >
                            <item.icon className={cn("w-5 h-5", isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-400")} />
                            {item.label}
                            {isActive && (
                                <motion.div
                                    layoutId="activeTab"
                                    className="absolute left-0 top-0 w-1 h-full bg-indigo-500 rounded-r-full"
                                />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* User / Footer */}
            <div className="p-4 border-t border-slate-900">
                <button className="flex items-center gap-3 px-4 py-3 w-full text-sm font-medium hover:text-white hover:bg-slate-900/50 rounded-lg transition-colors">
                    <Settings className="w-5 h-5" />
                    Settings
                </button>
                <div className="mt-4 flex items-center gap-3 px-4">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500" />
                    <div className="text-xs">
                        <div className="text-white font-bold">Creator One</div>
                        <div className="text-slate-600">Pro License</div>
                    </div>
                </div>
            </div>
        </aside>
    );
}
