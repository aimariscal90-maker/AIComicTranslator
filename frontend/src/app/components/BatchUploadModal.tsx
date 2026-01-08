"use client";

import { useState } from "react";
import { API_URL } from "@/config";

interface BatchUploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    selectedProject: string | null;
}

export default function BatchUploadModal({ isOpen, onClose, selectedProject }: BatchUploadModalProps) {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [zipFile, setZipFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState({ current: 0, total: 0 });
    // const [jobIds, setJobIds] = useState<string[]>([]); // Removed unused state

    if (!isOpen) return null;

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);

        // Separar archivos especiales (ZIP/PDF/CBR/CBZ) de imágenes
        const specialFiles = files.filter(f =>
            f.name.endsWith('.zip') ||
            f.name.endsWith('.pdf') ||
            f.name.endsWith('.cbr') ||
            f.name.endsWith('.cbz')
        );
        const images = files.filter(f => f.type.startsWith('image/'));

        if (specialFiles.length > 0) {
            setZipFile(specialFiles[0]); // Solo el primero
            setSelectedFiles([]);
        } else {
            setSelectedFiles(images);
            setZipFile(null);
        }
    };

    const uploadBatch = async () => {
        if (!selectedProject) {
            alert("Selecciona un proyecto primero");
            return;
        }

        if (selectedFiles.length === 0 && !zipFile) {
            alert("Selecciona archivos o un ZIP");
            return;
        }

        setUploading(true);

        try {
            const formData = new FormData();

            if (zipFile) {
                formData.append('zip_file', zipFile);
            } else {
                selectedFiles.forEach(file => {
                    formData.append('files', file);
                });
            }

            const response = await fetch(`${API_URL}/projects/${selectedProject}/upload-batch`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();

            // Validar que la respuesta tenga los campos esperados
            if (!data.job_ids || !Array.isArray(data.job_ids)) {
                console.error('[BATCH] Invalid response:', data);
                throw new Error('Invalid response from server: missing job_ids array');
            }


            setProgress({ current: 0, total: data.total_pages });

            // Polling para progreso
            pollProgress(data.job_ids);

        } catch (error) {
            console.error('Batch upload failed:', error);
            alert(`Error al subir archivos: ${(error as any).message || String(error)}`);
            setUploading(false);
        }
    };

    const pollProgress = async (jobIds: string[]) => {
        const checkJobs = async () => {
            let completed = 0;

            for (const jobId of jobIds) {
                try {
                    const response = await fetch(`${API_URL}/jobs/${jobId}`);
                    const job = await response.json();

                    if (job.status === 'completed' || job.progress === 100) {
                        completed++;
                    }
                } catch (e) {
                    // Ignorar errores de jobs individuales
                }
            }

            setProgress(prev => ({ ...prev, current: completed }));

            if (completed >= jobIds.length) {
                // Todos completados
                setUploading(false);
                alert(`¡Batch completado! ${completed} páginas procesadas`);
                onClose();
                // Recargar página para ver resultados
                window.location.reload();
            } else {
                // Seguir polling
                setTimeout(checkJobs, 2000);
            }
        };

        checkJobs();
    };

    const removeFile = (index: number) => {
        setSelectedFiles(files => files.filter((_, i) => i !== index));
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold">📦 Upload Masivo</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 text-2xl"
                    >
                        ✕
                    </button>
                </div>

                {!uploading ? (
                    <>
                        <div className="mb-4">
                            <label className="block text-sm font-semibold mb-2">
                                Selecciona archivos o ZIP/PDF/CBR/CBZ:
                            </label>
                            <input
                                type="file"
                                accept="image/*,.zip,.pdf,.cbr,.cbz"
                                multiple
                                onChange={handleFileSelect}
                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Soporta: Imágenes, ZIP, PDF, CBR, CBZ
                            </p>
                        </div>

                        {zipFile && (
                            <div className="mb-4 p-4 bg-blue-50 rounded">
                                <p className="font-semibold">
                                    {zipFile.name.endsWith('.pdf') ? '📄 PDF' :
                                        zipFile.name.endsWith('.cbr') ? '📚 CBR' :
                                            zipFile.name.endsWith('.cbz') ? '📘 CBZ' : '📦 ZIP'} seleccionado:
                                </p>
                                <p className="text-sm text-gray-700">{zipFile.name}</p>
                                <p className="text-xs text-gray-500">
                                    {(zipFile.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        )}

                        {selectedFiles.length > 0 && (
                            <div className="mb-4">
                                <p className="font-semibold mb-2">
                                    📁 Archivos seleccionados: {selectedFiles.length}
                                </p>
                                <div className="max-h-60 overflow-y-auto space-y-1">
                                    {selectedFiles.map((file, i) => (
                                        <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                                            <span>
                                                {i + 1}. {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                                            </span>
                                            <button
                                                onClick={() => removeFile(i)}
                                                className="text-red-500 hover:text-red-700"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex gap-2">
                            <button
                                onClick={uploadBatch}
                                disabled={selectedFiles.length === 0 && !zipFile}
                                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                            >
                                🚀 Procesar Todo
                            </button>
                            <button
                                onClick={onClose}
                                className="px-4 py-3 bg-gray-200 rounded hover:bg-gray-300"
                            >
                                Cancelar
                            </button>
                        </div>
                    </>
                ) : (
                    <div className="text-center">
                        <p className="text-xl font-semibold mb-4">
                            Procesando páginas...
                        </p>
                        <p className="text-3xl font-bold text-blue-600 mb-4">
                            {progress.current} / {progress.total}
                        </p>
                        <div className="w-full bg-gray-200 rounded-full h-4">
                            <div
                                className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                                style={{ width: `${(progress.current / progress.total) * 100}%` }}
                            />
                        </div>
                        <p className="text-sm text-gray-500 mt-2">
                            Por favor espera... Esto puede tomar varios minutos.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
