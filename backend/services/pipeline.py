import os
import cv2
import numpy as np
import uuid

def execute_lab_pipeline(
    image_path, 
    bubbles, 
    ocr_service, 
    translator, 
    style_analyzer, 
    font_matcher, 
    remover, 
    renderer, 
    upload_dir, 
    unique_filename,
    log_func=print
):
    """
    Lab Pipeline Logic (Copied Verbatim from main.py debug_pipeline).
    Used for Basic Translation to strictly enforce identical results.
    Includes Timing Instrumentation.
    """
    import time
    timings = {}
    total_start = time.time()
    
    img_cv = cv2.imread(image_path)
    
    # 2-PASS APPROACH FOR CONTEXT AWARENESS (Exact Lab Logic)
    processed_items = []
    texts_to_translate = []
    results = []
    render_bubbles = []
    
    # PASS 1: OCR & Prep
    log_func(f"[LabPipeline] Pass 1: OCR & Data Collection...")
    t_start = time.time()
    
    for i, b in enumerate(bubbles):
        # ROI Crop
        x1, y1, x2, y2 = map(int, b['bbox'])
        h, w = img_cv.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        crop = img_cv[y1:y2, x1:x2]
        
        step_data = {
            "id": i,
            "bbox": b['bbox'],
            "ocr_text": "Error/Empty",
            "translation": "", 
            "trans_provider": "Pending",
            "style": {},
            "font_match": "Pending",
            "crop_url": ""
        }
        
        if crop.size > 0:
            # OCR
            success, encoded = cv2.imencode('.jpg', crop)
            if success:
                try:
                    res = ocr_service.detect_text(encoded.tobytes())
                    text = res.get('text', '')
                    step_data['ocr_text'] = text
                    
                    current_words = []
                    if 'word_boxes' in res:
                        bx, by = x1, y1
                        for poly in res['word_boxes']:
                            # Global coords
                            global_poly = [[pt[0] + bx, pt[1] + by] for pt in poly]
                            current_words.append(global_poly)
                    
                    if text.strip():
                        processed_items.append({
                            'index': i,
                            'bubble': b,
                            'crop': crop,
                            'text': text,
                            'current_words': current_words,
                            'step_data': step_data
                        })
                        texts_to_translate.append(text)
                    else:
                         results.append(step_data) # Empty bubble result
                except Exception as e:
                     log_func(f"[LabPipeline] OCR Error {i}: {e}")
                     step_data['ocr_text'] = f"Error: {e}"
                     results.append(step_data)
        else:
             results.append(step_data)
    
    timings['ocr_processing'] = round(time.time() - t_start, 2)

    # PASS 2: BATCH TRANSLATION
    log_func(f"[LabPipeline] Pass 2: Batch Translation ({len(texts_to_translate)} items)...")
    t_start = time.time()
    batch_translations = []
    provider = "None"
    
    if texts_to_translate:
        if translator:
            try:
                 batch_translations, provider = translator.translate_batch_with_context(texts_to_translate)
            except Exception as e:
                 log_func(f"[LabPipeline] Batch Trans Failed: {e}")
                 provider = "Error"
                 batch_translations = [{'translation': t, 'type': 'speech'} for t in texts_to_translate]
        else:
            provider = "Disabled"
            batch_translations = [{'translation': t, 'type': 'speech'} for t in texts_to_translate]
    
    timings['translation'] = round(time.time() - t_start, 2)

    # PASS 3: STYLE & RENDER
    log_func(f"[LabPipeline] Pass 3: Style, Type & Render...")
    t_start = time.time()
    
    for idx, item in enumerate(processed_items):
        try:
            b = item['bubble']
            step_data = item['step_data']
            crop = item['crop']
            text = item['text']
            
            # Get Translation
            trans_item = batch_translations[idx] if idx < len(batch_translations) else {'translation': text, 'type': 'speech'}
            translation = trans_item.get('translation', text)
            b_type = trans_item.get('type', 'speech')
            
            step_data['translation'] = translation
            step_data['trans_provider'] = provider
            step_data['bubble_type'] = b_type

            # Style
            style = style_analyzer.analyze_roi(img_cv, b['bbox'], b.get('polygon'))
            step_data['style'] = style
            
            # Font Match
            font = font_matcher.match_font(style, b_type, crop, text)
            step_data['font_match'] = font
            
            # Mask (Skipping IO)
            mask, _ = style_analyzer._binarize_otsus(crop)
            
            # Render Prep
            rb = b.copy()
            # CRITICAL: Replicate Lab Logic of dumping style dict into bubble
            rb.update(style)
            rb['font'] = font
            rb['translation'] = translation
            rb['text_color'] = style.get('text_color', '#000000')
            rb['word_boxes'] = item['current_words']
            
            render_bubbles.append(rb)
            results.append(step_data)
        except Exception as e:
            log_func(f"[LabPipeline] Processing Error Bubble {item['index']}: {e}")
            results.append(item['step_data'])
        
    timings['analysis_rendering_prep'] = round(time.time() - t_start, 2)
    
    # Sort results
    results.sort(key=lambda x: x['id'])

    # --- PHASE 3: PREVIEW GENERATION ---
    
    final_url = None
    clean_url = None
    log_func(f"[LabPipeline] Render Bubbles Count: {len(render_bubbles)}")
    
    clean_name = f"clean_text_{unique_filename}"
    clean_path = os.path.join(upload_dir, clean_name)
    final_name = f"final_{unique_filename}"
    final_path = os.path.join(upload_dir, final_name)
    
    # Inpainting Timer
    t_start = time.time()
    if len(render_bubbles) > 0:
        try:
             # 1. Inpaint
             log_func("[LabPipeline] Starting Inpainting...")
             if remover.model is None:
                 log_func("[LabPipeline] ERROR: TextRemover model is None!")
             
             # mask_mode='text' from debug_pipeline
             remover.remove_text(image_path, render_bubbles, clean_path, mask_mode='text')
             
             if not os.path.exists(clean_path):
                  log_func(f"[LabPipeline] ERROR: Clean file not created at {clean_path}")
        except Exception as e:
             log_func(f"[LabPipeline] Inpainting failed: {e}")
    
    timings['inpainting'] = round(time.time() - t_start, 2)
    
    # Rendering Timer
    t_start = time.time()
    if len(render_bubbles) > 0 and os.path.exists(clean_path):
         try:
            # 2. Render
            log_func("[LabPipeline] Starting Rendering...")
            renderer.render_text(clean_path, render_bubbles, final_path)
            final_url = f"/uploads/{final_name}"
            clean_url = f"/uploads/{clean_name}"
            log_func(f"[LabPipeline] Final saved at: {final_path}")
         except Exception as re:
            log_func(f"[LabPipeline] Render error: {re}")
    
    timings['text_rendering'] = round(time.time() - t_start, 2)
    
    timings['total_time'] = round(time.time() - total_start, 2)

    return {
        "final_path": final_path,
        "clean_path": clean_path,
        "bubbles": bubbles, 
        "bubbles_data": results,
        "timings": timings
    }
