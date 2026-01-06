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
