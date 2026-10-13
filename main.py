import translators as ts
import sys

# Fix Unicode output for Tamil characters on Windows
sys.stdout.reconfigure(encoding="utf-8")

print("English to Tamil Translator")
print("Type 'exit' to quit")

while True:
    text = input("\nEnter English text: ").strip()

    if not text:
        continue

    if text.lower() == "exit":
        print("Translator closed.")
        break

    try:
        translated_text = ts.translate_text(text, translator="bing", from_language="en", to_language="ta")
        print("Tamil Translation:", translated_text)

    except Exception as e:
        print(f"Translation failed: {e}")