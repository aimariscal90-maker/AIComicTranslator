import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env vars from backend/.env
load_dotenv()

class TranslatorService:
    def __init__(self, target_lang='es'):
        self.target_lang = target_lang
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found in .env. Translation will fail.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Available models: gemini-flash-latest (Usually 1.5 Flash)
                # Usamos el alias latest para asegurar compatibilidad free tier
                self.model = genai.GenerativeModel('gemini-flash-latest')
                print("Gemini Translator initialized successfully (Model: gemini-flash-latest).")
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.model = None

    def translate(self, text):
        """
        Translates text to Spanish using Gemini LLM.
        Returns: (translated_text, provider_name)
        """
        if not text or not text.strip():
            return "", "None"
            
        if not self.model:
            print("Gemini model not initialized.")
            # Fallback direct
            try:
                from deep_translator import GoogleTranslator
                fallback = GoogleTranslator(source='auto', target='es')
                return fallback.translate(text), "Google Translate (Basic)"
            except:
                return text, "Error"

        try:
            # Try Gemini First
            try:
                # Prompt Engineering para comics
                prompt = (
                    f"Act as a professional comic book translator. "
                    f"Translate the following text from English (or source language) to Spanish (Spain). "
                    f"Keep the translation concise to fit in a speech bubble. "
                    f"Maintain the slang, tone, and character voice. "
                    f"If the text is a Sound Effect (SFX) or Onomatopoeia (e.g. BOOM, SPLASH), prepend '[SFX] ' to the translation. "
                    f"Do NOT add explanations, notes, or quotes. Just the translation (with optional tag). "
                    f"Text: \"{text}\""
                )
                
                response = self.model.generate_content(prompt)
                translated_text = response.text.strip()
                
                # Limpieza extra: A veces LLMs añaden comillas
                if translated_text.startswith('"') and translated_text.endswith('"'):
                    translated_text = translated_text[1:-1]
                    
                return translated_text, "Gemini Flash (AI)"
                
            except Exception as e:
                print(f"Gemini Translation error (Quota/Auth): {e}")
                print("Falling back to Google Translate (deep-translator)...")
                
                # Fallback
                from deep_translator import GoogleTranslator
                fallback = GoogleTranslator(source='auto', target='es')
                return fallback.translate(text), "Google Translate (Fallback)"
                
        except Exception as e:
            print(f"Global Translation error: {e}")
            return text, "Error"

    def translate_batch_with_context(self, texts_list):
        """
        Traduce una lista de textos manteniendo coherencia contextual.
        
        Input: ["Hello!", "How are you?", "Fine, thanks!"]
        Output: ["¡Hola!", "¿Qué tal?", "¡Bien, gracias!"]
        
        Día 24: Traducción con contexto de página completa.
        """
        if not texts_list or not any(t.strip() for t in texts_list):
            return [""] * len(texts_list), "None"
        
        if not self.model:
            # Fallback a traducción individual si no hay modelo
            print("Gemini not available, falling back to individual translation...")
            results = [self.translate(text)[0] for text in texts_list]
            return results, "Google Translate (Batch Fallback)"
        
        try:
            # Formatear textos con números
            texts_formatted = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts_list) if text.strip()])
            
            # Prompt contextual mejorado
            prompt = f"""Act as a professional comic book translator specialized in manga/comics.

Translate the following dialogues from English (or source language) to Spanish (Spain).

IMPORTANT RULES:
- Maintain CONSISTENT TONE between related dialogues (formal/informal)
- Preserve slang, sarcasm, and humor
- Keep character voice consistency
- For sound effects (SFX/onomatopoeia like BOOM, SPLASH), prepend '[SFX]'
- Be concise to fit speech bubbles
- Translate naturally, not literally

Dialogues to translate:
{texts_formatted}

Respond ONLY with the translations, one per line, in the SAME ORDER.
Do NOT include line numbers, explanations, or extra text.
Just the pure translations."""

            response = self.model.generate_content(prompt)
            translations_text = response.text.strip()
            
            # Parsear respuesta (limpiar números si los añadió)
            lines = translations_text.split('\n')
            translations = []
            
            for line in lines:
                # Limpiar números al inicio (ej: "1. Hola" -> "Hola")
                cleaned = line.strip()
                if cleaned and cleaned[0].isdigit():
                    # Quitar "1. " o "1) " o "1 - "
                    parts = cleaned.split('. ', 1)
                    if len(parts) > 1:
                        cleaned = parts[1]
                    else:
                        parts = cleaned.split(') ', 1)
                        if len(parts) > 1:
                            cleaned = parts[1]
                
                translations.append(cleaned)
            
            # Asegurarse de que tenemos el mismo número de traducciones
            while len(translations) < len(texts_list):
                translations.append("")
            
            return translations[:len(texts_list)], "Gemini Flash (Contextual)"
            
        except Exception as e:
            print(f"Batch translation error: {e}")
            print("Falling back to individual translation...")
            # Fallback a traducción individual
            results = [self.translate(text)[0] for text in texts_list]
            return results, "Gemini Flash (Individual Fallback)"

    def classify_bubbles_batch(self, texts_list):
        """
        Clasifica el tipo de cada bocadillo usando reglas heurísticas + LLM.
        
        Input: ["Hello!", "BOOM!", "I think..."]
        Output: ["speech", "sfx", "thought"]
        
        Día 25: Clasificación híbrida (reglas + LLM).
        """
        if not texts_list or not any(t.strip() for t in texts_list):
            return ["speech"] * len(texts_list)
        
        classifications = []
        
        # Lista de onomatopeyas comunes
        sfx_patterns = [
            'boom', 'bang', 'crash', 'splash', 'pow', 'bam', 'thud', 'wham',
            'crack', 'snap', 'pop', 'whoosh', 'zoom', 'swoosh', 'zzz',
            'kaboom', 'smash', 'clang', 'clink', 'buzz', 'hiss', 'thump',
            'slam', 'clack', 'tick', 'tock', 'drip', 'beep', 'ring'
        ]
        
        for text in texts_list:
            text_clean = text.strip()
            text_lower = text_clean.lower()
            
            # REGLA 1: Vacío → speech
            if not text_clean:
                classifications.append("speech")
                continue
            
            # REGLA 2: Onomatopeyas obvias (SFX)
            # Si el texto es solo una palabra y coincide con patrones de sonido
            words = text_clean.split()
            if len(words) <= 2:  # Máximo 2 palabras
                is_sfx = False
                for word in words:
                    word_lower = word.lower().strip('!?.,')
                    if word_lower in sfx_patterns:
                        is_sfx = True
                        print(f"[CLASSIFY DEBUG] '{text_clean}' → SFX (matched: {word_lower})")
                        break
                
                if is_sfx:
                    classifications.append("sfx")
                    continue
            
            # REGLA 3: TODO MAYÚSCULAS + corto + exclamaciones → SHOUT o SFX
            if text_clean.isupper() and len(text_clean) <= 20:
                # Si tiene patrón de sonido → SFX
                is_sound = any(pattern in text_lower for pattern in sfx_patterns)
                if is_sound:
                    print(f"[CLASSIFY DEBUG] '{text_clean}' → SFX (uppercase + sound pattern)")
                    classifications.append("sfx")
                else:
                    # Si tiene exclamaciones múltiples → SHOUT
                    if text_clean.count('!') >= 2 or '!!' in text_clean:
                        print(f"[CLASSIFY DEBUG] '{text_clean}' → SHOUT (uppercase + exclamations)")
                        classifications.append("shout")
                    else:
                        print(f"[CLASSIFY DEBUG] '{text_clean}' → SFX (uppercase + short)")
                        classifications.append("sfx")  # Asumir SFX si es corto y mayúsculas
                continue
            
            # REGLA 4: Palabras clave de narración
            narration_starts = ['meanwhile', 'later', 'earlier', 'the next', 'back at', 'that night', 'hours later']
            if any(text_lower.startswith(keyword) for keyword in narration_starts):
                print(f"[CLASSIFY DEBUG] '{text_clean}' → NARRATION")
                classifications.append("narration")
                continue
            
            # REGLA 5: Pensamiento (keywords)
            thought_keywords = ['i think', 'i wonder', 'maybe i', 'i should', 'what if', 'i must']
            if any(keyword in text_lower for keyword in thought_keywords):
                print(f"[CLASSIFY DEBUG] '{text_clean}' → THOUGHT")
                classifications.append("thought")
                continue
            
            # Si no coincide con reglas → speech por defecto
            print(f"[CLASSIFY DEBUG] '{text_clean}' → SPEECH (default)")
            classifications.append("speech")
        
        print(f"[CLASSIFY SUMMARY] Total: {len(classifications)}, Types: {set(classifications)}")
        return classifications
