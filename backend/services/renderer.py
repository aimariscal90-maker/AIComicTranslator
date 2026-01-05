import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import numpy as np

class TextRenderer:
    def __init__(self, font_path=None):
        # Por ahora usamos una fuente por defecto del sistema o una de Pillow si no hay una especifica
        self.font_path = font_path # "arial.ttf" por ejemplo si estuviera disponible

    def render_text(self, image_path, bubbles, output_path):
        """
        Dibuja el texto traducido sobre la imagen limpia.
        """
        try:
            # Abrir imagen
            with Image.open(image_path).convert("RGBA") as img:
                draw = ImageDraw.Draw(img)
                
                # Canvas para textos (para medir)
                txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
                draw_txt = ImageDraw.Draw(txt_layer)

                for bubble in bubbles:
                    text_content = bubble.get('translation', '')
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
                    # 1. Definir margenes de seguridad (para parches redondeados)
                    padding_ratio = 0.1 # 10% de margen a cada lado
                    max_w_px = w * (1.0 - padding_ratio * 2) 
                    max_h_px = h * (1.0 - padding_ratio * 2)
                    
                    font_size = int(h / 3) # Empezar optimista
                    min_font_size = 8
                    
                    final_wrapped_lines = []
                    final_font = None
                    final_line_heights = []
                    
                    # Bucle de reducción de fuente
                    while font_size >= min_font_size:
                        font = self._load_font(font_size)
                        
                        # Intentar wrapear a max_w_px con esta fuente
                        wrapped_lines = self._wrap_text_pixels(text_content, font, max_w_px, draw_txt)
                        
                        # Calcular altura total
                        line_heights = [draw_txt.textbbox((0, 0), line, font=font)[3] - draw_txt.textbbox((0, 0), line, font=font)[1] for line in wrapped_lines]
                        # Sumar alturas + un poco de leading (20% de font size)
                        leading = int(font_size * 0.2)
                        total_text_height = sum(line_heights) + (len(wrapped_lines) - 1) * leading
                        
                        if total_text_height <= max_h_px:
                            # CABE!
                            final_wrapped_lines = wrapped_lines
                            final_font = font
                            final_line_heights = line_heights
                            break
                        else:
                            font_size -= 2 # Reducir
                    
                    # Fallback si no cabe ni con min_size
                    if final_font is None:
                        font_size = min_font_size
                        final_font = self._load_font(font_size)
                        final_wrapped_lines = self._wrap_text_pixels(text_content, final_font, max_w_px, draw_txt)
                        # Recalcular alturas para fallback
                        final_line_heights = [draw_txt.textbbox((0, 0), line, font=final_font)[3] - draw_txt.textbbox((0, 0), line, font=final_font)[1] for line in final_wrapped_lines]

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
                    bg_color_rgb = bubble.get('bg_color', (255, 255, 255))
                    bg_color_rgba = (bg_color_rgb[0], bg_color_rgb[1], bg_color_rgb[2], 245)
                    
                    # Hacemos el parche un poco más grande que el texto real
                    patch_padding = 1
                    bg_x1 = center_x - real_max_w // 2 - patch_padding
                    bg_y1 = text_start_y - patch_padding
                    bg_x2 = center_x + real_max_w // 2 + patch_padding
                    bg_y2 = text_start_y + total_h + patch_padding
                    
                    # Dibujar parche (Rounded Rectangle para suavizar esquinas)
                    # Radio dinámico: 20% de la altura o 10px, lo que sea menor
                    radius = min(10, (bg_y2 - bg_y1) * 0.3)
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
            print(f"Error rendering text: {e}")
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

    def _load_font(self, size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
             try:
                 return ImageFont.load_default()
             except:
                 return ImageFont.load_default()
