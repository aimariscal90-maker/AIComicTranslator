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
        Clasifica el tipo de cada bocadillo usando LLM.
        
        Input: ["Hello!", "BOOM!", "I think..."]
        Output: ["speech", "sfx", "thought"]
        
        Día 25: Clasificación automática por tipo.
        """
        if not texts_list or not any(t.strip() for t in texts_list):
            return ["speech"] * len(texts_list)
        
        if not self.model:
            # Sin modelo LLM, asumir speech
            return ["speech"] * len(texts_list)
        
        try:
            # Formatear textos con números
            texts_formatted = "\n".join([f"{i+1}. {text[:50]}" for i, text in enumerate(texts_list) if text.strip()])
            
            # Prompt de clasificación mejorado (Day 25 v3 - More Examples)
            prompt = f"""You are a comic book expert. Classify each text into EXACTLY ONE category.

IMPORTANT RULES:
1. SFX: ONLY if it's a sound effect/onomatopoeia (BOOM, SPLASH, BANG, CRACK, whoosh, zzz)
2. NARRATION: ONLY if it's clearly narrator text (starts with "Meanwhile", "Later", "The next day", or describes scene)
3. SHOUT: ONLY if ALL CAPS and expressing strong emotion (not just emphasis)
4. THOUGHT: ONLY if clearly internal monologue (uses "I think", "I wonder", "Maybe I should")
5. SPEECH: Everything else (default for dialogue)

WHEN IN DOUBT → use "speech"

Examples:

SFX (sound effects):
- "BOOM" → sfx
- "SPLASH" → sfx  
- "BANG!" → sfx
- "Crack" → sfx
- "whoosh" → sfx
- "zzz..." → sfx
- "CRASH!" → sfx
- "BAM" → sfx
- "POW!" → sfx
- "Thud" → sfx

SPEECH (normal dialogue):
- "Hello there" → speech
- "You're late!" → speech
- "What happened?" → speech  
- "I don't know" → speech
- "Let's go" → speech
- "Really?" → speech
- "Come on!" → speech
- "Wait for me" → speech
- "That's amazing" → speech
- "I agree" → speech

SHOUT (all caps + emotion):
- "WHAT?!" → shout
- "NOOO!!" → shout
- "AAAHHH!" → shout
- "STOP!" → shout
- "HELP!" → shout
- "GET OUT!" → shout
- "I WON'T LET YOU!" → shout

NARRATION (narrator):
- "Meanwhile, in the city..." → narration
- "Later that day..." → narration
- "The next morning..." → narration
- "Back at headquarters..." → narration
- "Two hours earlier..." → narration

THOUGHT (internal):
- "I think I should go" → thought
- "Maybe I'm wrong..." → thought
- "I wonder what happened" → thought
- "What should I do?" → thought (if clearly internal)

Texts to classify:
{texts_formatted}

Respond with ONLY the category names, one per line:"""

            response = self.model.generate_content(prompt)
            classifications_text = response.text.strip()
            
            # Parsear respuesta
            lines = classifications_text.split('\n')
            classifications = []
            
            valid_types = ["speech", "thought", "shout", "narration", "sfx"]
            
            for line in lines:
                cleaned = line.strip().lower()
                
                # Extraer solo la categoría si hay texto extra
                for valid_type in valid_types:
                    if valid_type in cleaned:
                        classifications.append(valid_type)
                        break
                else:
                    # Default a speech si no se encuentra categoría válida
                    classifications.append("speech")
            
            # Asegurar mismo número de clasificaciones
            while len(classifications) < len(texts_list):
                classifications.append("speech")
            
            return classifications[:len(texts_list)]
            
        except Exception as e:
            print(f"Bubble classification error: {e}")
            # Fallback: asumir todo speech
            return ["speech"] * len(texts_list)
