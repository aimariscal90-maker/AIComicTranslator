from deep_translator import GoogleTranslator

class TranslatorService:
    def __init__(self, target_lang='es'):
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source='auto', target=target_lang)

    def translate(self, text):
        """
        Translates text to Spanish.
        """
        if not text or not text.strip():
            return ""
            
        try:
            # Limpieza basica (saltos de linea extraños del OCR)
            clean_text = text.replace('\n', ' ').strip()
            translated = self.translator.translate(clean_text)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original if fail
