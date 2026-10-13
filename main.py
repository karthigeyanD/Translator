import sys
import time
import os
import tempfile

import speech_recognition as sr
import pygame
from gtts import gTTS
from deep_translator import GoogleTranslator

# ── Unicode output for Tamil characters on Windows ───────────────────────────
sys.stdout.reconfigure(encoding="utf-8")

# ── pygame mixer init (for audio playback) ───────────────────────────────────
pygame.mixer.init()

# ── Speech recogniser setup ──────────────────────────────────────────────────
recogniser = sr.Recognizer()
recogniser.pause_threshold = 1.0   # seconds of silence = phrase end
recogniser.energy_threshold = 300  # mic sensitivity

def listen() -> str | None:
    """Listen from the microphone, return recognised English text or None."""
    with sr.Microphone() as source:
        print("🎙  Adjusting for ambient noise… please wait.")
        recogniser.adjust_for_ambient_noise(source, duration=1)
        print("🎙  Listening… (speak now)")
        try:
            audio = recogniser.listen(source, timeout=8, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("⚠  No speech detected. Try again.\n")
            return None

    print("🔄  Recognising…")
    try:
        return recogniser.recognize_google(audio, language="en-IN")
    except sr.UnknownValueError:
        print("⚠  Could not understand the audio. Try again.\n")
        return None
    except sr.RequestError as e:
        print(f"⚠  Speech recognition service error: {e}\n")
        return None

# ── TTS: speak using gTTS → temp mp3 → pygame ───────────────────────────────
def speak(text: str, lang: str = "en") -> None:
    """Convert text to speech and play it; cleans up the temp file after."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name

        gTTS(text=text, lang=lang).save(tmp_path)

        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        os.remove(tmp_path)
    except Exception as e:
        print(f"⚠  TTS error: {e}")

# ── Translator setup ─────────────────────────────────────────────────────────
# GoogleTranslator returns proper Tamil Unicode script (e.g. உங்களுடைய பெயர் என்ன).
# A 1-second sleep before each call keeps us well under Google's rate limit.
translator = GoogleTranslator(source="en", target="ta")

def translate(text: str, retries: int = 3) -> str:
    """Translate with exponential-backoff retry on transient errors."""
    for attempt in range(1, retries + 1):
        try:
            time.sleep(1)   # stay under Google's 5 req/s free limit
            result = translator.translate(text)
            return result
        except Exception as e:
            if attempt < retries:
                wait = attempt * 2
                print(f"⚠  Translation attempt {attempt} failed. Retrying in {wait}s…")
                time.sleep(wait)
            else:
                raise

# ── Main loop ────────────────────────────────────────────────────────────────
def main() -> None:
    banner = "English to Tamil Voice Translator"
    print(f"\n{'=' * len(banner)}")
    print(banner)
    print(f"{'=' * len(banner)}")
    print("Say 'exit' or 'quit' to stop.\n")

    speak("English to Tamil Voice Translator is ready. Please speak in English.", lang="en")

    while True:
        english_text = listen()

        if english_text is None:
            continue

        print(f"📝  You said: {english_text}")

        if english_text.lower().strip() in ("exit", "quit", "stop"):
            farewell = "Goodbye! Translator closed."
            print(farewell)
            speak(farewell, lang="en")
            break

        try:
            tamil_text = translate(english_text)
            print(f"🔤  Tamil Translation: {tamil_text}")

            # Speak English echo first
            speak(f"You said: {english_text}", lang="en")

            # Speak Tamil translation with Tamil TTS voice
            speak(tamil_text, lang="ta")

        except Exception as e:
            print(f"⚠  Translation failed: {e}")
            speak("Translation failed. Please try again.", lang="en")

        print()

if __name__ == "__main__":
    main()