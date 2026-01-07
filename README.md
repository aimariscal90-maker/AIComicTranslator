# 🦸‍♂️ AI Comic Translator

**AI Comic Translator** es una herramienta avanzada que permite traducir cómics, mangas y novelas gráficas de forma automática utilizando Inteligencia Artificial.

![Screenshot](https://via.placeholder.com/800x400?text=AI+Comic+Translator+Screenshot)

## ✨ Características Principales

- **🔍 Detección Inteligente:** Utiliza **YOLOv8** y **OpenCV** para localizar bocadillos de texto y segmentarlos con precisión.
- **🧠 OCR & Traducción:** 
  - OCR potente mediante **Google Cloud Vision** o Tesseract.
  - Traducción contextual con **Google Gemini 1.5 Flash** (LLM), respetando onomatopeyas y slang.
- **🎨 Inpainting (Borrado Mágico):** Utiliza **LaMa (Large Mask Inpainting)** para borrar el texto original y reconstruir el fondo del dibujo.
- **✍️ Renderizado & Edición:** 
  - Renderizado automático con fuentes estilo cómic (Comic Neue, Anime Ace).
  - **Editor Interactivo:** Haz clic en cualquier bocadillo para corregir el texto o cambiar la fuente sin perder el fondo.
- **⚡ Procesamiento Asíncrono:** Cola de tareas en segundo plano para no bloquear la interfaz.
- **📦 Exportación:** Descarga tu obra en JPG de alta calidad o bájate el proyecto completo en ZIP.

---

## 🚀 Instalación y Uso (Windows)

#### Requisitos Previos
- Python 3.10+
- Node.js 18+
- [Opcional] GPU NVIDIA para mayor velocidad en Inpainting.

#### Opción A: Instalación Automática (Recomendada)
1. **Clona el repositorio** o descarga el código.
2. Ejecuta **`install.bat`** (doble clic). 
   - *Esto creará el entorno virtual, instalará dependencias de Python y Node.js.*
3. Configura tus claves:
   - Renombra `backend/.env.example` a `.env`.
   - Añade tu `GEMINI_API_KEY`.
4. Ejecuta **`start-app.bat`**.
   - *Se abrirán dos ventanas negras (Backend y Frontend) y tu navegador en `http://localhost:3000`.*

#### Opción B: Docker (Avanzado)
1. Asegúrate de tener Docker Desktop corriendo.
2. Configura `backend/.env`.
3. Ejecuta:
   ```bash
   docker-compose up --build
   ```
4. Abre `http://localhost:3000`.

---

## 🛠️ Tecnologías

### Backend (Python / FastAPI)
- **FastAPI:** API REST de alto rendimiento.
- **Ultralytics YOLOv8:** Detección de objetos.
- **LaMa (Inpainting):** Red neuronal para reconstrucción de imágenes.
- **Google Generative AI:** Traducción con LLM.
- **OpenCV / Pillow:** Procesamiento de imágenes.

### Frontend (TypeScript / Next.js)
- **Next.js 13+ (App Router):** Framework moderno de React.
- **TailwindCSS:** Estilos y diseño responsivo.
- **React Compare Image:** Slider interactivo.

---

## 📝 Créditos
Proyecto desarrollado como parte del "20-Day AI Coding Challenge".
Creado por **Antigravity**.

*Nota: Para fuentes premium como "WildWords", añade el archivo `.ttf` en `backend/assets/fonts/`.*
