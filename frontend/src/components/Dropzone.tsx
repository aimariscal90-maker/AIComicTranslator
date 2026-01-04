"use client";

import { useState, useCallback } from "react";

interface DropzoneProps {
  onFileSelected: (file: File) => void;
}

export default function Dropzone({ onFileSelected }: DropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        onFileSelected(files[0]);
      }
    },
    [onFileSelected]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        onFileSelected(e.target.files[0]);
      }
    },
    [onFileSelected]
  );

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-4 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors
        ${
          isDragging
            ? "border-blue-500 bg-blue-50 text-blue-700"
            : "border-gray-300 hover:border-gray-400 text-gray-500"
        }`}
    >
      <input
        type="file"
        accept="image/*"
        className="hidden"
        id="fileInput"
        onChange={handleChange}
      />
      <label htmlFor="fileInput" className="cursor-pointer block w-full h-full">
        <div className="flex flex-col items-center justify-center space-y-2">
          <svg
            className="w-12 h-12"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <span className="text-lg font-medium">
            Arrasrta tu cómic aquí o haz click para seleccionar
          </span>
          <span className="text-sm">Soporta JPG, PNG</span>
        </div>
      </label>
    </div>
  );
}
