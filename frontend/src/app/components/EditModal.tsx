"use client";

import { useState, useEffect } from "react";

interface EditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (newText: string, newFont: string) => void;
  initialText: string;
  initialFont?: string;
}

export default function EditModal({
  isOpen,
  onClose,
  onSave,
  initialText,
  initialFont = "ComicNeue",
}: EditModalProps) {
  const [text, setText] = useState(initialText);
  const [font, setFont] = useState(initialFont);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setText(initialText);
      setFont(initialFont || "ComicNeue");
      setIsSaving(false);
    }
  }, [isOpen, initialText, initialFont]);

  if (!isOpen) return null;

  const handleSave = () => {
    setIsSaving(true);
    onSave(text, font);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
          <h3 className="text-white text-lg font-bold flex items-center gap-2">
            ✏️ Editar Bocadillo
          </h3>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          
          {/* Text Input */}
          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700">
              Traducción
            </label>
            <textarea
              className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none text-gray-800 font-medium"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Escribe el texto aquí..."
            />
          </div>

          {/* Font Selector */}
          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700">
              Tipografía
            </label>
            <div className="relative">
              <select
                value={font}
                onChange={(e) => setFont(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg appearance-none bg-white text-gray-800 focus:ring-2 focus:ring-blue-500 outline-none cursor-pointer"
              >
                <option value="ComicNeue">Comic Neue (Default)</option>
                <option value="AnimeAce">Anime Ace (Estilo Manga)</option>
                <option value="WildWords">Wild Words (Pro)</option>
              </select>
              <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-gray-500">
                ▼
              </div>
            </div>
            {font === "WildWords" && (
               <p className="text-xs text-amber-600 mt-1">
                 ⚠️ Requiere licencia "wildwords.ttf" en backend.
               </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t border-gray-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSaving}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-md transition-colors flex items-center gap-2"
          >
            {isSaving ? "Regenerando..." : "Guardar y Renderizar"}
          </button>
        </div>

      </div>
    </div>
  );
}
