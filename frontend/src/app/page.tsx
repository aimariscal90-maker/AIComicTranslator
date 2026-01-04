"use client";

import { useState } from "react";
import Dropzone from "@/components/Dropzone";
import ImagePreview from "@/components/ImagePreview";

interface UploadResponse {
  filename: string;
  url: string;
  original_name: string;
}

interface ApiResponse {
  status: string;
  original_url: string;
  debug_url: string;
  clean_url?: string;
  bubbles_count: number;
  bubbles_data: Array<{
    bbox: number[];
    confidence: number;
    class: number;
    text?: string;
    translation?: string;
  }>;
}

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [serverImage, setServerImage] = useState<string | null>(null);
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);

  const handleFileSelected = async (file: File) => {
    // 1. Mostrar preview local inmediato
    const objectUrl = URL.createObjectURL(file);
    setLocalPreview(objectUrl);
    setServerImage(null); // Reset server image
    setApiResponse(null);
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
      // La API devuelve: original_url, debug_url, clean_url
      if (data.debug_url) {
        const fullUrl = `http://localhost:8000${data.debug_url}`;
        setServerImage(fullUrl);
        console.log("Process success. Bubbles:", data.bubbles_count, data);
      } else {
        // Fallback por si acaso
        const fullUrl = `http://localhost:8000${data.original_url || (data as any).url}`;
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
              {isUploading && <span className="text-sm font-normal text-blue-500 animate-pulse">Procesando (Vision + OCR + Translating)...</span>}
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
                        <h3 className="text-sm font-bold text-gray-700">✨ Borrado Mágico</h3>
                      </div>
                      <div className="border border-purple-200 rounded-lg overflow-hidden relative shadow-sm">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={`http://localhost:8000${apiResponse.clean_url}`}
                          alt="Cleaned Image"
                          className="w-full h-auto"
                        />
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
                      <div key={idx} className="bg-gray-50 p-3 rounded border-l-4 border-indigo-500 text-sm shadow-sm">
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
                            <span className="text-xs uppercase text-green-600 font-bold tracking-wider">Español 🇪🇸</span>
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
                  Procesamiento completo.
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
    </main>
  );
}

