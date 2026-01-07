"use client";

import { useState } from "react";
import Dropzone from "@/components/Dropzone";
import ImagePreview from "@/components/ImagePreview";
import EditModal from "@/app/components/EditModal";

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
  const [isUploading, setIsUploading] = useState(false);
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [serverImage, setServerImage] = useState<string | null>(null);
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);

  // Interactive Editing State
  const [editingBubble, setEditingBubble] = useState<{ index: number; text: string; font?: string } | null>(null);
  const [imgDims, setImgDims] = useState<{ w: number; h: number } | null>(null);

  const handleFileSelected = async (file: File) => {
    // 1. Mostrar preview local inmediato
    const objectUrl = URL.createObjectURL(file);
    setLocalPreview(objectUrl);
    setServerImage(null);
    setApiResponse(null);
    setImgDims(null);
    setIsUploading(true);

    try {
      // 2. Subir al backend
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data: ApiResponse = await response.json();
      setApiResponse(data);

      // 3. Mostrar imagen procesada (Debug con cajas)
      if (data.debug_url) {
        const fullUrl = `http://localhost:8000${data.debug_url}`;
        setServerImage(fullUrl);
      } else {
        const fullUrl = `http://localhost:8000${data.original_url}`;
        setServerImage(fullUrl);
      }

    } catch (error) {
      console.error("Error uploading:", error);
      alert("Error al subir la imagen. Asegúrate de que el Backend está corriendo en puerto 8000.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            AI Comic Translator
          </h1>
          <p className="text-gray-600">
            Laboratorio de Traducción Automatizada
          </p>
        </header>

        {/* Upload Section */}
        <section className="bg-white p-6 rounded-xl shadow-sm">
          <Dropzone onFileSelected={handleFileSelected} />
        </section>

        {/* Main Grid: Pipeline Stages */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Input Stage */}
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <span>1. Entrada</span>
              {isUploading && <span className="text-sm font-normal text-blue-500 animate-pulse">Procesando (Vision + OCR + Translating + Double Inpainting)...</span>}
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

                {/* Grid de Resultados */}
                <div className="grid grid-cols-1 gap-8">
                  {/* Debug View */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded">PASO 1</span>
                      <h3 className="text-sm font-bold text-gray-700">Detección & OCR</h3>
                    </div>
                    <ImagePreview src={serverImage} alt="Debug View" />
                  </div>

                  {/* Clean View */}
                  {apiResponse?.clean_url && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold bg-purple-100 text-purple-700 px-2 py-0.5 rounded">PASO 2</span>
                        <h3 className="text-sm font-bold text-gray-700">✨ Borrado (Limpieza)</h3>
                      </div>
                      <div className="border border-purple-200 rounded-lg overflow-hidden relative shadow-sm">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={`http://localhost:8000${apiResponse.clean_url}`}
                          alt="Cleaned Image"
                          className="w-full h-auto opacity-80"
                        />
                      </div>
                    </div>
                  )}

                  {/* FINAL RESULT */}
                  {apiResponse?.final_url && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold bg-green-100 text-green-700 px-2 py-0.5 rounded">PASO 3 (FINAL)</span>
                        <h3 className="text-sm font-bold text-gray-700">🎨 Resultado Final (Español) - Click para Editar</h3>
                      </div>

                      <div className="relative inline-block w-full border-2 border-green-500 rounded-lg overflow-hidden shadow-lg">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={`http://localhost:8000${apiResponse.final_url}`}
                          alt="Final Image"
                          className="w-full h-auto block"
                          onLoad={(e) => {
                            setImgDims({ w: e.currentTarget.naturalWidth, h: e.currentTarget.naturalHeight });
                          }}
                        />

                        {/* OVERLAY DIVS FOR INTERACTION */}
                        {imgDims && apiResponse.bubbles_data.map((bubble, idx) => {
                          const [x1, y1, x2, y2] = bubble.bbox;
                          const width = x2 - x1;
                          const height = y2 - y1;

                          // Calculate % positions
                          const left = (x1 / imgDims.w) * 100;
                          const top = (y1 / imgDims.h) * 100;
                          const wPct = (width / imgDims.w) * 100;
                          const hPct = (height / imgDims.h) * 100;

                          return (
                            <div
                              key={idx}
                              onClick={() => setEditingBubble({ index: idx, text: bubble.translation || "", font: bubble.font || "ComicNeue" })}
                              className="absolute border-2 border-transparent hover:border-blue-500 hover:bg-blue-500/10 cursor-pointer transition-all z-10 group"
                              style={{
                                left: `${left}%`,
                                top: `${top}%`,
                                width: `${wPct}%`,
                                height: `${hPct}%`,
                              }}
                              title="Clic para editar"
                            >
                              {/* Tooltip on hover */}
                              <div className="hidden group-hover:block absolute -top-8 left-1/2 -translate-x-1/2 bg-black/75 text-white text-xs px-2 py-1 rounded whitespace-nowrap pointer-events-none">
                                ✎ Editar
                              </div>
                            </div>
                          );
                        })}

                        <div className="absolute bottom-2 right-2 flex gap-2 z-20 pointer-events-none">
                          <a
                            href={`http://localhost:8000${apiResponse.final_url}`}
                            download
                            className="bg-green-600 hover:bg-green-700 text-white text-xs px-3 py-1.5 rounded-full font-bold shadow-md transition-colors pointer-events-auto"
                          >
                            ⬇ Descargar
                          </a>
                        </div>
                      </div>

                      {/* Global Font Control */}
                      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-gray-700">Cambiar Fuente Global:</span>
                          <select
                            className="p-2 border border-gray-300 rounded text-sm bg-white text-gray-900 font-medium focus:ring-2 focus:ring-blue-500 outline-none"
                            onChange={async (e) => {
                              if (!apiResponse || !confirm("¿Aplicar esta fuente a TODOS los bocadillos?")) return;

                              const newFont = e.target.value;
                              try {
                                const response = await fetch(`http://localhost:8000/process/${apiResponse.id}/update-all-fonts`, {
                                  method: "PATCH",
                                  headers: { "Content-Type": "application/json" },
                                  body: JSON.stringify({ font: newFont })
                                });

                                if (!response.ok) throw new Error("Bulk Update failed");

                                const data = await response.json();
                                const timestamp = new Date().getTime();
                                const newFinalUrl = `${data.final_url}?t=${timestamp}`;

                                setApiResponse(prev => {
                                  if (!prev) return null;
                                  // Updates all bubbles in local state too
                                  const newBubbles = prev.bubbles_data.map(b => ({ ...b, font: newFont }));
                                  return {
                                    ...prev,
                                    final_url: newFinalUrl,
                                    bubbles_data: newBubbles
                                  };
                                });
                              } catch (error) {
                                console.error(error);
                                alert("Error al actualizar fuentes");
                              }
                            }}
                          >
                            <option value="">Seleccionar...</option>
                            <option value="ComicNeue">Comic Neue</option>
                            <option value="AnimeAce">Anime Ace</option>
                            <option value="WildWords">Wild Words</option>
                          </select>
                        </div>
                      </div>

                    </div>
                  )}
                </div>

                {/* OCR & Translation Results Panel */}
                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
                  <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex justify-between items-center">
                    <h3 className="font-semibold text-gray-700">📜 Traducción Detectada</h3>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                      {apiResponse?.bubbles_count || 0} bubbles
                    </span>
                  </div>
                  <div className="max-h-[400px] overflow-y-auto p-4 space-y-4">
                    {apiResponse?.bubbles_data?.map((bubble, idx) => (
                      <div key={idx} className="bg-gray-50 p-3 rounded border-l-4 border-indigo-500 text-sm shadow-sm hover:bg-indigo-50 cursor-pointer" onClick={() => setEditingBubble({ index: idx, text: bubble.translation || "", font: bubble.font || "ComicNeue" })}>
                        <div className="flex justify-between text-xs text-gray-500 mb-2">
                          <span className="font-mono font-bold">Bubble #{idx + 1}</span>
                          <span>Conf: {(bubble.confidence * 100).toFixed(1)}%</span>
                        </div>

                        <div className="space-y-2">
                          {/* Original */}
                          <div>
                            <span className="text-xs uppercase text-gray-400 font-bold tracking-wider">Original</span>
                            <p className="text-gray-800 font-medium whitespace-pre-wrap bg-white p-2 rounded border border-gray-100 mt-1">
                              {bubble.text ? bubble.text : <span className="text-gray-400 italic">(Vacio)</span>}
                            </p>
                          </div>

                          {/* Translation */}
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs uppercase text-green-600 font-bold tracking-wider">Español 🇪🇸</span>
                              {bubble.translation_provider && (
                                <span className={`text-[10px] px-1.5 rounded border ${bubble.translation_provider.includes("Gemini")
                                  ? "bg-purple-100 text-purple-700 border-purple-200"
                                  : "bg-gray-100 text-gray-600 border-gray-200"
                                  }`}>
                                  {bubble.translation_provider}
                                </span>
                              )}
                            </div>
                            <p className="text-green-800 font-bold whitespace-pre-wrap bg-green-50 p-2 rounded border border-green-100 mt-1">
                              {bubble.translation ? bubble.translation : <span className="text-gray-400 italic">...</span>}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-2 bg-green-50 text-green-700 text-sm rounded border border-green-200">
                  Procesamiento completo. Haz clic en la imagen para editar.
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[300px] border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center text-gray-400 bg-gray-50">
                La imagen procesada aparecerá aquí
              </div>
            )}
          </div>
        </section>
      </div>

      <EditModal
        isOpen={!!editingBubble}
        onClose={() => setEditingBubble(null)}
        initialText={editingBubble?.text || ""}
        initialFont={editingBubble?.font || "ComicNeue"}
        onSave={async (newText, newFont) => {
          if (!editingBubble || !apiResponse) return;

          try {
            const response = await fetch(`http://localhost:8000/process/${apiResponse.id}/update-bubble`, {
              method: "PATCH",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                bubble_index: editingBubble.index,
                new_text: newText,
                font: newFont
              })
            });

            if (!response.ok) throw new Error("Update failed");

            const data = await response.json();

            // Force re-render with new URL (Timestamp hash)
            const timestamp = new Date().getTime();
            const newFinalUrl = `${data.final_url}?t=${timestamp}`;

            setApiResponse(prev => {
              if (!prev) return null;
              const newBubbles = [...prev.bubbles_data];
              newBubbles[editingBubble.index] = {
                ...newBubbles[editingBubble.index],
                translation: newText,
                font: newFont
              };
              return {
                ...prev,
                final_url: newFinalUrl,
                bubbles_data: newBubbles
              };
            });

            setEditingBubble(null);

          } catch (e) {
            console.error(e);
            alert("Error al actualizar");
          }
        }}
      />
    </main>
  );
}
