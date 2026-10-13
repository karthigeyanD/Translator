from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="en", target="ta")

print("English to Tamil Translator")
print("Type 'exit' to quit")

while True:
    text = input("\nEnter English text: ")

    if text.lower() == "exit":
        print("Translator closed.")
        break

    try:
        translated_text = translator.translate(text)
        print("Tamil Translation:", translated_text)

    except Exception as e:
        print("Translation failed. Check your internet connection.")