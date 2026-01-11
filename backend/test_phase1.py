
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def test_binarization_and_contours():
    """
    Day 01: Lab & Binarization
    Objetivo: Aislar las letras del fondo usando Otsu y obtener contornos.
    """
    
    # 1. Cargar Golden Test Image (o una zona simulada)
    # Para este test, usaremos un recorte simulado si no existe, o la imagen real.
    input_path = "golden_test.png"
    if not os.path.exists(input_path):
        print(f"❌ No se encontró {input_path}. Asegúrate de haber ejecutado la preparación.")
        return

    img = cv2.imread(input_path)
    if img is None:
        print(f"❌ Error al leer {input_path}.")
        return

    print(f"✅ Imagen cargada: {img.shape}")

    # Simulemos que el detector ya nos dio un ROI (Region of Interest)
    # Coordenadas aproximadas de un globo de texto en la imagen de ejemplo (ajustar si es necesario)
    # Por ahora tomamos toda la imagen como si fuera un recorte grande para probar
    roi = img.copy()

    # --- PASO 1: BINARIZACIÓN (Otsu) ---
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Otsu automático
    thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print(f"🔹 Umbral Otsu detectado: {thresh_val}")

    # --- PASO 2: DETECCIÓN DE FONDO (Dark vs Light) ---
    # Heurística: Si los bordes son blancos, el fondo es blanco (texto negro).
    # Si los bordes son negros, el fondo es negro (texto blanco).
    mask_h, mask_w = binary.shape
    border_pixels = np.concatenate([
        binary[0, :], binary[-1, :], binary[:, 0], binary[:, -1]
    ])
    median_border = np.median(border_pixels)
    
    is_dark_bg = median_border < 127
    if is_dark_bg:
        print("🌙 Fondo Oscuro detectado (Texto Claro)")
        # El texto ya es blanco (255) en binary, así que binary es la máscara correcta
        text_mask = binary
    else:
        print("☀️ Fondo Claro detectado (Texto Oscuro)")
        # El texto es negro (0) en binary, invertimos para que sea la máscara
        text_mask = cv2.bitwise_not(binary)

    # --- PASO 3: LIMPIEZA DE RUIDO ---
    # Kernel para morfología
    kernel = np.ones((2,2), np.uint8)
    text_mask = cv2.morphologyEx(text_mask, cv2.MORPH_OPEN, kernel) # Eliminar ruido pequeño

    # --- PASO 4: CONTORNOS (Letter Extraction) ---
    contours, hierarchy = cv2.findContours(text_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"🔤 Contornos (letras/formas) encontrados: {len(contours)}")

    # Visualización
    debug_vis = roi.copy()
    cv2.drawContours(debug_vis, contours, -1, (0, 0, 255), 1) # Rojo para contornos

    # Guardar resultados
    cv2.imwrite("test_phase1_binary.png", text_mask)
    cv2.imwrite("test_phase1_contours.png", debug_vis)
    
    print("💾 Resultados guardados: test_phase1_binary.png, test_phase1_contours.png")

if __name__ == "__main__":
    test_binarization_and_contours()
