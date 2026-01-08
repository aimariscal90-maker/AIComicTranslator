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
        Clasifica el tipo de cada bocadillo usando SOLO Gemini LLM con JSON.
        
        Input: ["Hello!", "BOOM!", "I think..."]
        Output: ["speech", "sfx", "thought"]
        
        Día 25 v2: LLM puro con prompt agresivo + JSON.
        """
        if not texts_list or not any(t.strip() for t in texts_list):
            return ["speech"] * len(texts_list)
        
        if not self.model:
            print("[CLASSIFY] Gemini not available, defaulting all to speech")
            return ["speech"] * len(texts_list)
        
        try:
            # Formatear textos con índices para el LLM
            texts_formatted = "\n".join([f"{i+1}. \"{text[:80]}\"" for i, text in enumerate(texts_list)])
            
            # Prompt agresivo y optimizado
            prompt = f"""You are an expert comic book analyst. Classify each text into EXACTLY ONE category.

CRITICAL: Be AGGRESSIVE with classification. Don't default to "speech" - look for patterns!

Categories:
- "sfx": ANY sound effect or onomatopoeia (BOOM, whoosh, crack, zzzz, drip, etc.)
- "shout": Text in ALL CAPS expressing strong emotion (WHAT?!, NOOO!!, STOP!!)
- "narration": Scene descriptions, time/location indicators (Meanwhile..., Later..., The city...)
- "thought": Internal monologue, questions to self (I think..., What if..., Maybe I...)
- "speech": Only clear character dialogue

RULES FOR SFX:
- If it's a single word in caps → likely SFX
- If it sounds like a sound → SFX
- Common patterns: BOOM, BANG, CRASH, SPLASH, WHOOSH, SNAP, CRACK, POP, THUD, SLAM, etc.

RULES FOR SHOUT:
- ALL CAPS + punctuation (!!, ?!) → SHOUT
- Emotional outbursts → SHOUT

Texts to classify:
{texts_formatted}

Respond with ONLY a valid JSON array of categories, nothing else.
Example: ["speech", "sfx", "shout", "speech", "narration"]

JSON array:"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            print(f"[CLASSIFY LLM] Raw response: {response_text[:200]}")
            
            # Limpiar respuesta: quitar markdown, espacios, etc.
            response_clean = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parsear JSON
            import json
            try:
                classifications = json.loads(response_clean)
                
                # Validar que sea una lista
                if not isinstance(classifications, list):
                    raise ValueError("Response is not a list")
                
                # Validar tipos
                valid_types = ["speech", "thought", "shout", "narration", "sfx"]
                classifications_clean = []
                for c in classifications:
                    c_lower = str(c).lower().strip()
                    if c_lower in valid_types:
                        classifications_clean.append(c_lower)
                    else:
                        classifications_clean.append("speech")
                
                # Asegurar mismo tamaño
                while len(classifications_clean) < len(texts_list):
                    classifications_clean.append("speech")
                
                result = classifications_clean[:len(texts_list)]
                print(f"[CLASSIFY LLM] Result: {dict((t, result.count(t)) for t in set(result))}")
                return result
                
            except json.JSONDecodeError as e:
                print(f"[CLASSIFY ERROR] JSON parse failed: {e}")
                print(f"[CLASSIFY ERROR] Response was: {response_clean}")
                # Fallback: intentar parsear línea por línea
                lines = response_clean.split('\n')
                classifications = []
                for line in lines:
                    line_clean = line.strip().strip('"').strip("'").strip(',').lower()
                    if line_clean in valid_types:
                        classifications.append(line_clean)
                
                if len(classifications) >= len(texts_list):
                    return classifications[:len(texts_list)]
                else:
                    return ["speech"] * len(texts_list)
                    
        except Exception as e:
            print(f"[CLASSIFY ERROR] Classification failed: {e}")
            import traceback
            traceback.print_exc()
            return ["speech"] * len(texts_list)
