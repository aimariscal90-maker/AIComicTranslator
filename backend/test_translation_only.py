from deep_translator import GoogleTranslator

def test_trans():
    text = "Hello world, this is a comic book test."
    print(f"Original: {text}")
    
    try:
        translator = GoogleTranslator(source='auto', target='es')
        res = translator.translate(text)
        print(f"Translated: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_trans()
