"use client";

import { useState, useEffect } from "react";
import { API_URL } from "@/config";
import BatchUploadModal from "@/app/components/BatchUploadModal";

export default function TestsPage() {
    const [apiStatus, setApiStatus] = useState<"loading" | "online" | "offline">("loading");
    const [showBatchModal, setShowBatchModal] = useState(false);

    // Check API Status on Mount
    useEffect(() => {
        checkApi();
    }, []);

    const checkApi = async () => {
        setApiStatus("loading");
        try {
            const res = await fetch(`${API_URL}/`);
            if (res.ok) {
                setApiStatus("online");
            } else {
                setApiStatus("offline");
            }
        } catch (e) {
            setApiStatus("offline");
        }
    };

    return (
        <main className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-4xl mx-auto space-y-8">
                <header className="border-b pb-6 mb-6">
                    <h1 className="text-3xl font-extrabold text-gray-800">🛠️ Panel de Pruebas (Tests)</h1>
                    <p className="text-gray-500">Verifica la funcionalidad de los componentes aislados.</p>
                </header>

                {/* TEST 1: API Connectivity */}
                <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-bold">1. Conectividad API (Backend)</h2>
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${apiStatus === 'online' ? 'bg-green-100 text-green-700' :
                                apiStatus === 'offline' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
                            }`}>
                            {apiStatus.toUpperCase()}
                        </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">
                        URL Configurada: <code className="bg-gray-100 px-2 py-1 rounded">{API_URL}</code>
                    </p>
                    <button
                        onClick={checkApi}
                        className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition"
                    >
                        🔄 Re-probar Conexión
                    </button>
                </section>

                {/* TEST 2: Batch Upload Modal */}
                <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-bold mb-2">2. Modal de Carga Masiva (Batch Upload)</h2>
                    <p className="text-sm text-gray-600 mb-4">
                        Prueba la apertura y cierre del modal de subida de archivos (CBZ, ZIP, Imágenes).
                        <br />
                        <span className="text-yellow-600">Nota: Requiere un proyecto existente para funcionar realmente.</span>
                    </p>
                    <button
                        onClick={() => setShowBatchModal(true)}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-bold"
                    >
                        🚀 Abrir Batch Modal
                    </button>

                    {/* Dummy Project ID needed for props, user should select one or we mock it */}
                    <BatchUploadModal
                        isOpen={showBatchModal}
                        onClose={() => setShowBatchModal(false)}
                        selectedProject="test-project-id"
                    />
                </section>

                {/* TEST 3: Navigation Links */}
                <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">3. Navegación Rápida</h2>
                    <div className="flex gap-4">
                        <a href="/" className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200">
                            🏠 Ir al Inicio
                        </a>
                        <a href="/dashboard" className="px-4 py-2 bg-purple-100 text-purple-700 rounded hover:bg-purple-200">
                            📊 Ir al Dashboard
                        </a>
                    </div>
                </section>

                {/* TEST 4: Environment Info */}
                <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">4. Información de Entorno</h2>
                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-xs">
                        {JSON.stringify({
                            NODE_ENV: process.env.NODE_ENV,
                            NEXT_PUBLIC_API_URL: API_URL,
                            TIMESTAMP: new Date().toISOString()
                        }, null, 2)}
                    </pre>
                </section>
            </div>
        </main>
    );
}
