"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/config";

interface Project {
    id: string;
    name: string;
    description: string | null;
    created_at: string;
    pages: any[];
}

export default function DashboardPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newProjectName, setNewProjectName] = useState("");
    const [newProjectDesc, setNewProjectDesc] = useState("");

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const res = await fetch(`${API_URL}/projects`);
            if (res.ok) {
                const data = await res.json();
                setProjects(data);
            }
        } catch (error) {
            console.error("Error fetching projects:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const createProject = async () => {
        try {
            const res = await fetch(`${API_URL}/projects`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: newProjectName,
                    description: newProjectDesc || null,
                }),
            });

            if (res.ok) {
                setShowCreateModal(false);
                setNewProjectName("");
                setNewProjectDesc("");
                fetchProjects();
            }
        } catch (error) {
            console.error("Error creating project:", error);
        }
    };

    const deleteProject = async (projectId: string) => {
        if (!confirm("¿Eliminar este proyecto? Se perderán todas las páginas.")) {
            return;
        }

        try {
            const res = await fetch(`${API_URL}/projects/${projectId}`, {
                method: "DELETE",
            });

            if (res.ok) {
                fetchProjects();
            }
        } catch (error) {
            console.error("Error deleting project:", error);
        }
    };

    return (
        <main className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                            Dashboard de Proyectos
                        </h1>
                        <p className="text-gray-600 mt-2">Gestiona tus cómics traducidos</p>
                    </div>

                    <div className="flex gap-4">
                        <Link
                            href="/"
                            className="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-bold transition-colors"
                        >
                            ← Traductor
                        </Link>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition-colors shadow-md"
                        >
                            + Nuevo Proyecto
                        </button>
                    </div>
                </div>

                {/* Projects Grid */}
                {isLoading ? (
                    <div className="text-center py-20 text-gray-500">Cargando proyectos...</div>
                ) : projects.length === 0 ? (
                    <div className="text-center py-20">
                        <p className="text-gray-500 text-lg mb-4">
                            No tienes proyectos aún
                        </p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold"
                        >
                            Crear tu primer proyecto
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {projects.map((project) => (
                            <div
                                key={project.id}
                                className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow p-6 border border-gray-100"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold text-gray-800 line-clamp-1">
                                        {project.name}
                                    </h3>
                                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-bold">
                                        {project.pages?.length || 0} páginas
                                    </span>
                                </div>

                                {project.description && (
                                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                                        {project.description}
                                    </p>
                                )}

                                <div className="text-xs text-gray-400 mb-4">
                                    Creado: {new Date(project.created_at).toLocaleDateString()}
                                </div>

                                <div className="flex gap-2">
                                    <Link
                                        href={`/project/${project.id}`}
                                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-bold text-center transition-colors"
                                    >
                                        Ver Proyecto
                                    </Link>
                                    <button
                                        onClick={() => deleteProject(project.id)}
                                        className="bg-red-100 hover:bg-red-200 text-red-700 px-4 py-2 rounded-lg text-sm font-bold transition-colors"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Create Project Modal */}
                {showCreateModal && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                        <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
                            <h2 className="text-2xl font-bold mb-4">Nuevo Proyecto</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        Nombre del Proyecto *
                                    </label>
                                    <input
                                        type="text"
                                        value={newProjectName}
                                        onChange={(e) => setNewProjectName(e.target.value)}
                                        placeholder="Ej: One Piece - Capítulo 1"
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        Descripción (opcional)
                                    </label>
                                    <textarea
                                        value={newProjectDesc}
                                        onChange={(e) => setNewProjectDesc(e.target.value)}
                                        placeholder="Agrega notas sobre este proyecto..."
                                        className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-3 mt-6">
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={createProject}
                                    disabled={!newProjectName.trim()}
                                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Crear
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
