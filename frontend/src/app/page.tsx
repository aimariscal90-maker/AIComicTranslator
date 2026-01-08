"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Dropzone from "@/components/Dropzone";
import ImagePreview from "@/components/ImagePreview";
import EditModal from "@/app/components/EditModal";
import ComparisonView from "@/app/components/ComparisonView";
import BatchUploadModal from "@/app/components/BatchUploadModal";
import { API_URL } from "@/config";

interface UploadResponse {
  filename: string;
  url: string;
  original_name: string;
}

interface ApiResponse {
  status: string;
  id: string; // Needed for update
  original_url: string;
  debug_url: string;
  clean_url?: string;
  clean_bubble_url?: string;
  clean_text_url?: string;
  final_url?: string;
  bubbles_count: number;
  bubbles_data: Array<{
    bbox: number[];
    confidence: number;
    class: number;
    text?: string;
    translation?: string;
    translation_provider?: string;
    font?: string; // Edit support
  }>;
}

export default function Home() {
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [serverImage, setServerImage] = useState<string | null>(null);

  // Polling State (Day 17)
  const [jobId, setJobId] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [viewMode, setViewMode] = useState<"split" | "compare">("split");
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingBubble, setEditingBubble] = useState<{ index: number, text: string, font: string } | null>(null);

  // Day 23: Project Selection
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");

  // Day 27: Batch Upload
  const [showBatchUpload, setShowBatchUpload] = useState(false);

  // Fetch projects on mount
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
    }
  };
  const [imgDims, setImgDims] = useState<{ w: number; h: number } | null>(null);
  const [fontSelector, setFontSelector] = useState("ComicNeue"); // Global Font Selector

  const pollJobStatus = async (id: string) => {
    try {
      const res = await fetch(`${API_URL}/jobs/${id}`);
      if (!res.ok) return; // Keep trying or handle error
      const job = await res.json();

      setProgress(job.progress || 0);
      setCurrentStep(job.step || "Procesando...");

      if (job.status === "completed") {
        setApiResponse(job.result);

        // Set Server Image Logic
        if (job.result.final_url) {
          setServerImage(`${API_URL}${job.result.final_url}`);
        } else if (job.result.debug_url) {
          setServerImage(`${API_URL}${job.result.debug_url}`);
        } else {
          setServerImage(`${API_URL}${job.result.original_url}`);
        }
        setIsUploading(false);
        setJobId(null); // Stop polling indicator logic
      } else if (job.status === "failed") {
        console.error("Job Failed:", job.error);
        alert(`Error en el proceso: ${job.error}`);
        setIsUploading(false);
        setJobId(null);
      } else {
        // Continue polling
        setTimeout(() => pollJobStatus(id), 1000);
      }
    } catch (e) {
      console.error("Polling error", e);
      // Retry in 2s
      setTimeout(() => pollJobStatus(id), 2000);
    }
  };

  const handleFileSelected = async (file: File) => {
    // 1. Mostrar preview local inmediato
    const objectUrl = URL.createObjectURL(file);
    setLocalPreview(objectUrl);
    setServerImage(null);
    setApiResponse(null);
    setImgDims(null);

    // Reset Polling UI
    setIsUploading(true);
    setProgress(0);
    setCurrentStep("Subiendo Imagen...");
    setJobId(null);
    setViewMode("split"); // Reset view mode on new file

    try {
      // 2. Subir al backend
      const formData = new FormData();
      formData.append("file", file);

      // Day 23: Include project_id if selected
      if (selectedProject) {
        formData.append("project_id", selectedProject);
      }

      const response = await fetch(`${API_URL}/process`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      // 3. Iniciar Polling si recibimos Job ID
      if (data.job_id) {
        setJobId(data.job_id);
        pollJobStatus(data.job_id);
      } else {
        // Fallback legacy (si el backend devuelve directo data, aunque ya no deberia)
        setApiResponse(data);
        setIsUploading(false);
      }

    } catch (error) {
      console.error("Error uploading:", error);
      alert("Error al subir la imagen. Asegúrate de que el Backend está corriendo en puerto 8000.");
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-2">
          <div className="flex justify-between items-center mb-4">
            <div className="flex-1"></div>
            <div className="flex-1">
              <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                AI Comic Translator
              </h1>
              <p className="text-gray-600">
                Laboratorio de Traducción Automatizada
              </p>
            </div>
            <div className="flex-1 flex justify-end">
              <Link
                href="/dashboard"
                className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition-colors shadow-md"
              >
                📁 Proyectos
              </Link>
            </div>
          </div>
        </header>

        {/* Project Selection (Day 23) */}
        <section className="bg-white p-4 rounded-xl shadow-sm">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            📁 Proyecto (opcional)
          </label>
          <select
            value={selectedProject || ""}
            onChange={(e) => setSelectedProject(e.target.value || null)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">Sin proyecto (temporal)</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-2">
            Selecciona un proyecto para guardar esta página permanentemente
          </p>

          {/* Day 27: Batch Upload Button */}
          {selectedProject && (
            <button
              onClick={() => setShowBatchUpload(true)}
              className="mt-3 w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg font-bold transition-all shadow-md flex items-center justify-center gap-2"
            >
              📦 Upload Masivo (Múltiples Imágenes o ZIP)
            </button>
          )}

          {/* Day 28: Export Buttons */}
          {selectedProject && (
            <div className="mt-4 flex gap-2">
              <a
                href={`${API_URL}/projects/${selectedProject}/export?format=pdf`}
                download
                className="flex-1 px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-lg font-bold text-center shadow-sm transition-colors flex items-center justify-center gap-2"
              >
                📄 Descargar PDF
              </a>
              <a
                href={`${API_URL}/projects/${selectedProject}/export?format=cbz`}
                download
                className="flex-1 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg font-bold text-center shadow-sm transition-colors flex items-center justify-center gap-2"
              >
                📚 Descargar CBZ
              </a>
            </div>
          )}
        </section>

        {/* Upload Section */}
        <section className="bg-white p-6 rounded-xl shadow-sm">
          <Dropzone onFileSelected={handleFileSelected} />
        </section>

        {/* Status Bar (Loading) */}
        {isUploading && (
          <div className="bg-white p-4 rounded-xl shadow-sm border border-blue-100">
            <div className="flex justify-between mb-2">
              <span className="text-blue-700 font-bold">{currentStep}</span>
              <span className="text-blue-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* View Mode Toggle & Downloads (Solo si hay resultado) */}
        {apiResponse?.final_url && !isUploading && (
          <div className="flex flex-col items-center gap-4">
            {/* View Toggles */}
            <div className="bg-white p-1 rounded-lg border shadow-sm inline-flex">
              <button
                onClick={() => setViewMode("split")}
                className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${viewMode === "split"
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-500 hover:bg-gray-50"
                  }`}
              >
                Vista Separada
              </button>
              <button
                onClick={() => setViewMode("compare")}
                className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${viewMode === "compare"
                  ? "bg-purple-100 text-purple-700"
                  : "text-gray-500 hover:bg-gray-50"
                  }`}
              >
                👁️ Comparar
              </button>
            </div>

            {/* Export Buttons */}
            <div className="flex gap-4">
              <a
                href={`${API_URL}/process/${apiResponse.id}/download-final`}
                download
                className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg shadow-md font-bold transition-transform hover:-translate-y-0.5 active:translate-y-0"
              >
                📥 Descargar Imagen
              </a>
              <a
                href={`${API_URL}/process/${apiResponse.id}/download-zip`}
                download
                className="flex items-center gap-2 px-5 py-2.5 bg-gray-800 hover:bg-gray-900 text-white rounded-lg shadow-md font-bold transition-transform hover:-translate-y-0.5 active:translate-y-0"
              >
                📦 Descargar ZIP
              </a>
            </div>
          </div>
        )}

        {/* COMPARISON VIEW MODE */}
        {viewMode === "compare" && apiResponse?.final_url && localPreview && (
          <section className="animate-fade-in-up">
            <ComparisonView
              leftImage={localPreview}
              rightImage={`${API_URL}${apiResponse.final_url}?t=${Date.now()}`}
            />
          </section>
        )}

        {/* SPLIT VIEW MODE (Classic) */}
        <div className={viewMode === "split" ? "block" : "hidden"}>
          <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Input Stage */}
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <span>1. Entrada</span>
              </h2>
              {localPreview && (
                <ImagePreview src={localPreview} alt="Original Image" />
              )}
            </div>

            {/* Result Stage */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-800">2. Resultados AI</h2>
              {serverImage ? (
                <div className="space-y-6">

                  {/* Global Font Control */}
                  <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
                    <label className="text-sm font-bold text-gray-700">Fuente Global:</label>
                    <select
                      className="p-2 border border-gray-300 rounded text-sm bg-white text-gray-900 font-medium focus:ring-2 focus:ring-blue-500 outline-none"
                      value={fontSelector}
                      onChange={(e) => setFontSelector(e.target.value)}
                    >
                      <option value="ComicNeue">Comic Neue</option>
                      <option value="AnimeAce">Anime Ace</option>
                      <option value="WildWords">Wild Words</option>
                    </select>
                    <button
                      className="bg-gray-800 text-white px-4 py-2 rounded text-sm font-bold hover:bg-gray-700 transition-colors"
                      onClick={async () => {
                        if (!apiResponse?.id) return;
                        try {
                          const res = await fetch(`${API_URL}/process/${apiResponse.id}/update-all-fonts`, {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ font: fontSelector })
                          });
                          if (res.ok) {
                            const data = await res.json();
                            // Force cache bust
                            const timestamp = Date.now();
                            setApiResponse(prev => prev ? ({ ...prev, final_url: data.final_url }) : null);
                            setServerImage(`${API_URL}${data.final_url}?t=${timestamp}`);
                          }
                        } catch (e) {
                          console.error(e);
                          alert("Error updating fonts");
                        }
                      }}
                    >
                      Aplicar a Todo
                    </button>
                  </div>

                  {/* Grid de Resultados */}
                  <div className="grid grid-cols-1 gap-8">
                    {/* Final Result View with Overlay */}
                    {apiResponse?.final_url && (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-bold bg-green-100 text-green-700 px-2 py-0.5 rounded">FINAL</span>
                          <h3 className="text-sm font-bold text-gray-700">🇪🇸 Traducción (Click para editar)</h3>
                        </div>

                        <div className="relative">
                          <div className="border border-green-200 rounded-lg overflow-hidden shadow-md group relative">
                            {/* Imagen Final */}
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={serverImage} // serverImage tracks the final_url with hacks
                              alt="Translated Comic"
                              className="w-full h-auto"
                              onLoad={(e) => {
                                const img = e.currentTarget;
                                setImgDims({ w: img.naturalWidth, h: img.naturalHeight });
                              }}
                            />

                            {/* Interactive Overlay */}
                            {/* Solo mostramos overlay si tenemos dimensiones (loaded) */}
                            {imgDims && apiResponse.bubbles_data.map((bubble, idx) => {
                              const [x1, y1, x2, y2] = bubble.bbox;
                              // Convert absolute coords to percentage
                              const left_perc = (x1 / imgDims.w) * 100;
                              const top_perc = (y1 / imgDims.h) * 100;
                              const width_perc = ((x2 - x1) / imgDims.w) * 100;
                              const height_perc = ((y2 - y1) / imgDims.h) * 100;

                              return (
                                <div
                                  key={idx}
                                  className="absolute border-2 border-transparent hover:border-blue-500 hover:bg-blue-500/20 cursor-pointer transition-all rounded-sm z-10 group-hover:border-dashed group-hover:border-blue-300/50"
                                  style={{
                                    left: `${left_perc}%`,
                                    top: `${top_perc}%`,
                                    width: `${width_perc}%`,
                                    height: `${height_perc}%`
                                  }}
                                  onClick={() => setEditingBubble({
                                    index: idx,
                                    text: bubble.translation || "",
                                    font: bubble.font || "ComicNeue"
                                  })}
                                  title="Click to edit text"
                                />
                              );
                            })}
                          </div>
                          <p className="text-xs text-gray-400 mt-1 text-center">💡 Haz click en los cuadros azules para editar el texto.</p>
                        </div>
                      </div>
                    )}

                    {/* Debug View */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded">PASO 1</span>
                        <h3 className="text-sm font-bold text-gray-700">Detección & OCR</h3>
                      </div>
                      {apiResponse?.debug_url && (
                        <div className="border border-blue-200 rounded-lg overflow-hidden relative shadow-sm opacity-70 hover:opacity-100 transition-opacity">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={`${API_URL}${apiResponse.debug_url}`}
                            alt="Debug View"
                            className="w-full h-auto"
                          />
                        </div>
                      )}
                    </div>


                  </div>
                </div>
              ) : (
                <div className="h-64 bg-gray-100 rounded-xl border-dashed border-2 border-gray-300 flex items-center justify-center text-gray-400">
                  <p>La traducción aparecerá aquí</p>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Edit Modal */}
        {editingBubble && apiResponse && (
          <EditModal
            isOpen={!!editingBubble}
            onClose={() => setEditingBubble(null)}
            initialText={editingBubble.text}
            initialFont={editingBubble.font || "ComicNeue"}
            onSave={async (newText, newFont) => {
              // Call API update
              try {
                const res = await fetch(`${API_URL}/process/${apiResponse.id}/update-bubble`, {
                  method: 'PATCH',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    bubble_index: editingBubble.index,
                    new_text: newText,
                    font: newFont
                  })
                });

                if (res.ok) {
                  const data = await res.json();
                  // Update local state to reflect change immediately if possible, or force reload
                  // Force image reload by updating URL with timestamp
                  const timestamp = Date.now();
                  setServerImage(`${API_URL}${data.final_url}?t=${timestamp}`);

                  // Update apiResponse data localy too
                  const updatedBubbles = [...apiResponse.bubbles_data];
                  updatedBubbles[editingBubble.index].translation = newText;
                  updatedBubbles[editingBubble.index].font = newFont;
                  setApiResponse({ ...apiResponse, bubbles_data: updatedBubbles, final_url: data.final_url });

                  setEditingBubble(null);
                } else {
                  alert("Failed to save changes");
                }
              } catch (e) {
                console.error(e);
                alert("Error saving changes");
              }
            }}
          />
        )}

        {/* Day 27: Batch Upload Modal */}
        <BatchUploadModal
          isOpen={showBatchUpload}
          onClose={() => setShowBatchUpload(false)}
          selectedProject={selectedProject}
        />

      </div>
    </main>
  );
}
