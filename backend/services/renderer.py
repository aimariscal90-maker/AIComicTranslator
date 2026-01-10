import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import numpy as np
from contextlib import contextmanager

class TextRenderer:
    def __init__(self, font_path=None):
        # Por ahora usamos una fuente por defecto del sistema o una de Pillow si no hay una especifica
        self.font_path = font_path # "arial.ttf" por ejemplo si estuviera disponible

    @contextmanager
    def _get_image_context(self, image_source):
        if isinstance(image_source, str):
            with Image.open(image_source) as img:
                yield img.convert("RGBA")
        else:
            yield image_source.convert("RGBA")

    def render_text(self, image_path, bubbles, output_path):
        """
        Dibuja el texto traducido sobre la imagen limpia.
        """
        try:
            # Abrir imagen (Soporte para str path o objeto PIL Image)
            with self._get_image_context(image_path) as img:
                draw = ImageDraw.Draw(img)
                
                # Canvas para textos (para medir)
                txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
                draw_txt = ImageDraw.Draw(txt_layer)

                for bubble in bubbles:
                    # Obtenemos la traduccion pero limpiamos la etiqueta [SFX] si existe para que no salga en la imagen
                    raw_trans = bubble.get('translation', '')
                    text_content = raw_trans.replace('[SFX] ', '').replace('[SFX]', '') # Doble limpieza por si acaso
                    
                    if not text_content:
                        continue
                        
                    # Coordenadas
                    x1, y1, x2, y2 = bubble['bbox']
                    w = x2 - x1
                    h = y2 - y1
                    
                    # Ignorar cajas muy enanas (ruido)
                    if w < 10 or h < 10:
                        continue

                    # --- ESTRATEGIA DE AJUSTE DE TEXTO (Pixel-Perfect) ---
                    
                    # 1. Detectar forma primero (para saber márgenes)
                    polygon = bubble.get('polygon', [])
                    is_rectangle = False
                    if polygon and len(polygon) > 2:
                        try:
                            poly_points = [(p[0], p[1]) for p in polygon]
                            
                            # Shoelace formula simple
                            x_coords = [p[0] for p in poly_points]
                            y_coords = [p[1] for p in poly_points]
                            area_poly = 0.5 * np.abs(np.dot(x_coords, np.roll(y_coords, 1)) - np.dot(y_coords, np.roll(x_coords, 1)))
                            area_bbox = w * h
                            
                            if area_bbox > 0:
                                ratio = area_poly / area_bbox
                                if ratio > 0.80: 
                                    is_rectangle = True
                        except Exception as e:
                            pass 

                    # 2. Definir margenes según forma
                    if is_rectangle:
                        # Para cuadrados: MÁXIMO espacio posible.
                        # Margen mínimo de 1-2px para no tocar el borde exacto
                        # Y restamos el padding del parche que se suma luego (patch_padding=2)
                        # Ancho Texto = Ancho Caja - (2 * patch_padding) - (2 * safety_margin)
                        # Digamos safety=1px. Total resta = 4px + 2px = 6px
                        max_w_px = w - 6 
                        max_h_px = h - 6
                    else:
                    # Para óvalos: Margen del 10% para curvatura
                        padding_ratio = 0.1 
                        max_w_px = w * (1.0 - padding_ratio * 2) 
                        max_h_px = h * (1.0 - padding_ratio * 2)
                    
                    # Obtener fuente deseada por el usuario (o Default)
                    font_name = bubble.get('font', 'ComicNeue')

                    # Size Strategy: Use estimated OR bounding box heuristic
                    estimated_size = bubble.get('estimated_font_size')
                    if estimated_size:
                        # Start slightly smaller than estimated (to fit translation which might be longer)
                        # Or start exact. Let's start exact.
                        font_size = int(estimated_size * 0.9) 
                    else:
                        font_size = int(h / 3) # Empezar optimista
                        
                    min_font_size = 8
                    
                    final_wrapped_lines = []
                    final_font = None
                    final_line_heights = []
                    
                    # Bucle de reducción de fuente
                    # Day 13 Refined: Shape-Aware Wrapping
                    # Bucle de reducción de fuente
                    # Day 13 Refined: Shape-Aware Wrapping
                    while font_size >= min_font_size:
                        font = self._load_font(font_size, font_name, bubble.get('font_path'))
                        
                        if is_rectangle:
                             # Estrategia Rectangular
                             wrapped_lines = self._wrap_text_pixels(text_content, font, max_w_px, draw_txt)
                             
                             # Validar altura
                             line_heights = [draw_txt.textbbox((0, 0), line, font=font)[3] - draw_txt.textbbox((0, 0), line, font=font)[1] for line in wrapped_lines]
                             leading = int(font_size * 0.2)
                             total_text_height = sum(line_heights) + (len(wrapped_lines) - 1) * leading
                             
                             if total_text_height <= max_h_px:
                                 # SI CABE
                                 final_wrapped_lines = wrapped_lines
                                 final_font = font
                                 final_line_heights = line_heights
                                 break
                             else:
                                 wrapped_lines = [] # Fallo
                        else:
                             # Estrategia Oval (Bocadillos de diálogo)
                             wrapped_lines = self._wrap_text_oval(text_content, font, w, h, draw_txt)
                        
                        if wrapped_lines:
                             # ÉXITO: El texto cabe en el óvalo con este tamaño de fuente
                             final_wrapped_lines = wrapped_lines
                             final_font = font
                             # Calculamos alturas para el renderizado posterior
                             final_line_heights = [draw_txt.textbbox((0, 0), line, font=font)[3] - draw_txt.textbbox((0, 0), line, font=font)[1] for line in wrapped_lines]
                             break
                        else:
                             # No cabe, probamos fuente mas pequeña
                             font_size -= 2 
                    
                    # Fallback si no cabe ni con min_size (usamos wrapping rectangular clásico a fuerza bruta)
                    if not final_wrapped_lines:
                        font_size = min_font_size
                        final_font = self._load_font(font_size, font_name, bubble.get('font_path'))
                        # Wrapping rectangular forzoso
                        max_w_fallback = w * 0.8
                        final_wrapped_lines = self._wrap_text_pixels(text_content, final_font, max_w_fallback, draw_txt)
                        final_line_heights = [draw_txt.textbbox((0, 0), line, font=final_font)[3] - draw_txt.textbbox((0, 0), line, font=final_font)[1] for line in final_wrapped_lines]
                        
                        # Fix for logic below needing real_max_w to be initialized
                        # Note: The original code logic proceeds to drawing. Need to ensure loops logic matches.

                    # --- DIBUJAR ---
                    leading = int(font_size * 0.2)
                    total_h = sum(final_line_heights) + (len(final_wrapped_lines) - 1) * leading
                    
                    # Centro del rectangulo
                    center_x = x1 + w // 2
                    center_y = y1 + h // 2
                    
                    # Origen de dibujo (top-left del bloque de texto completo)
                    text_start_y = center_y - total_h // 2
                    
                    # Calcular ancho máximo real del bloque (para el parche)
                    real_max_w = 0
                    for line in final_wrapped_lines:
                        bbox = draw_txt.textbbox((0, 0), line, font=final_font)
                        lw = bbox[2] - bbox[0]
                        if lw > real_max_w: real_max_w = lw

                    # PARCHE BLANCO (Fondo Adaptativo)
                    # Origen de dibujo (top-left del bloque de texto completo)
                    text_start_y = center_y - total_h // 2
                    
                    # Calcular ancho máximo real del bloque (para el parche)
                    real_max_w = 0
                    for line in final_wrapped_lines:
                        bbox = draw_txt.textbbox((0, 0), line, font=final_font)
                        lw = bbox[2] - bbox[0]
                        if lw > real_max_w: real_max_w = lw

                    # PARCHE BLANCO (Fondo Adaptativo con Feathering/Blur)
                    bg_color_rgb = bubble.get('bg_color', (255, 255, 255))
                    bg_color_rgba = (bg_color_rgb[0], bg_color_rgb[1], bg_color_rgb[2], 255) # Opacidad base alta para el blur
                    
                    # Aumentamos padding ligeramente
                    patch_padding = 2
                    bg_x1 = center_x - real_max_w // 2 - patch_padding
                    bg_y1 = text_start_y - patch_padding
                    bg_x2 = center_x + real_max_w // 2 + patch_padding
                    bg_y2 = text_start_y + total_h + patch_padding
                    
                    # Dibujar parche (Rounded Rectangle Solido sin Blur)
                    h_patch = bg_y2 - bg_y1
                    if is_rectangle:
                        # Para cajas cuadradas, radio pequeño
                        radius = 5
                    else:
                        # Para ovalos, radio grande para simular redondez
                        radius = int(min(10, h_patch * 0.3))
                    
                    draw.rounded_rectangle([bg_x1, bg_y1, bg_x2, bg_y2], radius=radius, fill=bg_color_rgba)

                    # Dibujar Texto
                    text_fill = bubble.get('text_color', (0, 0, 0))
                    if len(text_fill) == 3:
                        text_fill = (text_fill[0], text_fill[1], text_fill[2], 255)
                    else:
                        text_fill = (0, 0, 0, 255)

                    current_y = text_start_y
                    for i, line in enumerate(final_wrapped_lines):
                        # Centrar horizontalmente cada linea
                        bbox = draw_txt.textbbox((0, 0), line, font=final_font)
                        lw = bbox[2] - bbox[0]
                        line_x = center_x - lw // 2
                        
                        draw.text((line_x, current_y), line, font=final_font, fill=text_fill)
                        
                        current_y += final_line_heights[i] + leading

                # Guardar resultado
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(output_path, quality=95)
                return True

        except Exception as e:
            import traceback
            error_msg = f"Error rendering text: {e}\n{traceback.format_exc()}"
            print(error_msg)
            with open("render_error.log", "w") as f:
                f.write(error_msg)
            return False

    def _wrap_text_pixels(self, text, font, max_width, draw_ctx):
        """
        Wraps text into lines ensuring no line exceeds max_width (in pixels).
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Probar añadir palabra a linea actual
            test_line = ' '.join(current_line + [word])
            bbox = draw_ctx.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            
            if w <= max_width:
                current_line.append(word)
            else:
                # Si la palabra sola ya es mas larga que el ancho máx, la forzamos (o la partimos, pero complicamos)
                # Aquí la forzamos a una linea nueva si current_line tiene algo
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Caso muy raro: palabra gigante. La metemos igual para no perder info.
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

    def _wrap_text_oval(self, text, font, bubble_w, bubble_h, draw_ctx):
        """
        Wraps text into lines trying to fit into an oval shape defined by bubble_w and bubble_h.
        Iteratively tries increasing number of lines to fit the text.
        Returns list of strings if successful, or [] if it fails to fit even with max lines.
        """
        words = text.split()
        if not words:
            return []
            
        # Parametros de fuente
        bbox = draw_ctx.textbbox((0, 0), "Aj", font=font) # Altura de referencia
        line_height_raw = bbox[3] - bbox[1]
        leading = int(line_height_raw * 0.2)
        total_line_height = line_height_raw + leading
        
        # Radios de la elipse (con un margen de seguridad interno del 15%)
        # El 15% simula que el texto no toque los bordes curvos
        a = (bubble_w / 2) * 0.85 
        b = (bubble_h / 2) * 0.85
        
        # Intentar encajar en N líneas (de 1 a 20)
        # Si con N lineas la altura total excede el alto del globo, paramos.
        for num_lines in range(1, 21):
            # 1. Verificar altura total
            # Altura del bloque de texto = N * line_height - last_leading
            block_height = num_lines * total_line_height - leading
            if block_height > (b * 2):
                # Ya no cabe verticalmente
                break
                
            # 2. Calcular anchos disponibles para cada linea
            # Asumimos que el bloque de texto está centrado verticalmente en la elipse (y=0)
            # Calculamos la coordenada Y del centro de cada linea
            center_y_offset = (block_height / 2)
            
            # Vector de anchos permitidos por linea
            allowed_widths = []
            possible_config = True
            
            for i in range(num_lines):
                # Posicion Y relativa al centro de la elipse
                # i=0 es la linea superior. Su 'top' es -block_height/2.
                # Su centro es -block_height/2 + (total_line_height * i) + (line_height_raw/2)
                # Simplificación: mid_y de la linea i
                line_mid_y = (-block_height / 2) + (i * total_line_height) + (line_height_raw / 2)
                
                # Ecuacion elipse: x^2/a^2 + y^2/b^2 = 1  => x = a * sqrt(1 - y^2/b^2)
                # Ancho disponible = 2 * x based on y
                if abs(line_mid_y) >= b:
                    width_at_y = 0
                else:
                    width_at_y = 2 * a * np.sqrt(1 - (line_mid_y / b)**2)
                
                if width_at_y < 10: # Muy estrecho (arriba/abajo extremos)
                    possible_config = False
                    break
                allowed_widths.append(width_at_y)
            
            if not possible_config:
                continue
                
            # 3. Intentar verter las palabras en estos huecos
            current_lines = []
            word_idx = 0
            all_words_fit = True
            
            for line_idx in range(num_lines):
                if word_idx >= len(words):
                    break # Ya metimos todas
                    
                max_w_this_line = allowed_widths[line_idx]
                current_line_words = []
                
                while word_idx < len(words):
                    next_word = words[word_idx]
                    # Probar añadir
                    test_str = ' '.join(current_line_words + [next_word])
                    w_text = draw_ctx.textbbox((0, 0), test_str, font=font)[2] - draw_ctx.textbbox((0, 0), test_str, font=font)[0]
                    
                    if w_text <= max_w_this_line:
                        current_line_words.append(next_word)
                        word_idx += 1
                    else:
                        # No cabe, pasamos a siguiente linea
                        break
                        
                current_lines.append(' '.join(current_line_words))
            
            # Al terminar las lineas, ¿quedan palabras hueérfanas?
            if word_idx < len(words):
                # No cupo en esta configuración de N líneas
                continue # Probar con N+1
            else:
                # ÉXITO: Cupo todo
                return current_lines
                
        # Si salimos del bucle es que no se encontró configuración válida
        return []

    def _load_font(self, size, font_name="ComicNeue", explicit_path=None):
        """
        Carga una fuente.
        Prioridad:
        1. explicit_path (ruta absoluta .ttf)
        2. font_name mapping en backend/fonts
        3. Fallbacks
        """
        
        # 1. Ruta explicita del FontMatcher
        if explicit_path and os.path.exists(explicit_path):
            try:
                return ImageFont.truetype(explicit_path, size)
            except:
                pass # Fallback

        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
        
        # Mapa de Archivos (Legacy / Default)
        font_files = {
            "ComicNeue": "dialogue/ComicNeue-Bold.ttf", # Updated path structure
            "AnimeAce": "dialogue/animeace.ttf",
            "WildWords": "dialogue/CCWildWords-Roman.ttf",
            "Bangers": "sfx/Bangers-Regular.ttf",
            "Roboto": "narrator/Roboto-Medium.ttf"
        }
        
        target_file = font_files.get(font_name, "dialogue/ComicNeue-Bold.ttf")
        full_path = os.path.join(fonts_dir, target_file)

        # Prioridad 2: Fuente solicitada por nombre
        try:
            return ImageFont.truetype(full_path, size)
        except:
            # Fallback 1: Intentar ComicNeue si falló la otra
            try:
                fallback_path = os.path.join(fonts_dir, "dialogue/ComicNeue-Bold.ttf")
                return ImageFont.truetype(fallback_path, size)
            except:
                # Fallback final a Arial o Default
                try:
                    return ImageFont.truetype("arial.ttf", size)
                except:
                    return ImageFont.load_default()
