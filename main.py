import sys
import time
import os
import tempfile

import speech_recognition as sr
import pygame
from gtts import gTTS
import requests

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
# Uses the public Google Translate gtx endpoint directly via requests.
# This is the same endpoint the browser widget uses — stable, no API key
# required, and returns proper Tamil Unicode script.
_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
_TRANSLATE_PARAMS = {"client": "gtx", "sl": "en", "tl": "ta", "dt": "t"}

def translate(text: str, retries: int = 3) -> str:
    """Translate English → Tamil (Unicode script) with retry on errors."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(
                _TRANSLATE_URL,
                params={**_TRANSLATE_PARAMS, "q": text},
                timeout=10,
            )
            resp.raise_for_status()
            # Response structure: [[[translated, original, ...], ...], ...]
            translated = "".join(chunk[0] for chunk in resp.json()[0] if chunk[0])
            return translated
        except Exception as e:
            if attempt < retries:
                wait = attempt * 2
                print(f"⚠  Translation attempt {attempt} failed ({e}). Retrying in {wait}s…")
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