"use client";

import { useState } from "react";
import Dropzone from "@/components/Dropzone";
import ImagePreview from "@/components/ImagePreview";

interface UploadResponse {
  filename: string;
  url: string;
  original_name: string;
}

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [serverImage, setServerImage] = useState<string | null>(null);

  const handleFileSelected = async (file: File) => {
    // 1. Mostrar preview local inmediato
    const objectUrl = URL.createObjectURL(file);
    setLocalPreview(objectUrl);
    setServerImage(null); // Reset server image
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

      const data = await response.json();

      // 3. Mostrar imagen procesada (Debug con cajas)
      // La API devuelve: original_url, debug_url, clean_url
      if (data.debug_url) {
        const fullUrl = `http://localhost:8000${data.debug_url}`;
        setServerImage(fullUrl);
        console.log("Process success. Bubbles:", data.bubbles_count, data);
      } else {
         // Fallback por si acaso
         const fullUrl = `http://localhost:8000${data.original_url || data.url}`;
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
              {isUploading && <span className="text-sm font-normal text-blue-500 animate-pulse">Subiendo...</span>}
            </h2>
            {localPreview && (
              <ImagePreview src={localPreview} alt="Original Image" />
            )}
          </div>

          {/* Result Stage (Placeholder for now) */}
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-gray-800">2. Servidor (Round-trip)</h2>
            {serverImage ? (
              <div className="space-y-2">
                <ImagePreview src={serverImage} alt="Server Image" />
                <div className="p-2 bg-green-50 text-green-700 text-sm rounded border border-green-200">
                  Imagen guardada exitosamente en backend.
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

