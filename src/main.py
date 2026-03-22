import time
import json
import os
import sys

sys.path.insert(0, "/mnt/d/project_ss/src")

from tts_module import speak
from stt_module import listen_and_transcribe
from llm_module import ask_chintu, load_model
from wake_word_module import load_wake_word_model, wait_for_wake_word

# ── CONFIG ──────────────────────────────────────────────
PROFILE_PATH = "/mnt/d/project_ss/child_profile.json"

def load_profile():
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def run():
    print("=" * 50)
    print("  CHINTU AI TOY - Starting up...")
    print("=" * 50)

    profile  = load_profile()
    age      = profile.get("age", 3)
    language = profile.get("language", "telugu")
    name     = profile.get("child_name", "Babu")

    print(f"  Child: {name}, Age: {age}, Language: {language}")
    print("=" * 50)

    # Load all models at startup
    print("[MAIN] Loading AI brain...")
    load_model()

    print("[MAIN] Loading wake word model...")
    wake_model = load_wake_word_model(use_custom=False)

    print("[MAIN] Chintu is ready!")
    speak("Namaskaram! Nenu Chintu. Meeru ela unnaru?", language)

    print("\n[MAIN] Say 'Hey Jarvis' to wake Chintu")
    print("[MAIN] Press Ctrl+C to stop\n")
    print("[MAIN] TIP: Type question directly and press Enter to skip voice\n")

    while True:
        try:
            # ── SLEEP — wait for wake word ────────────────
            print("[MAIN] Sleeping... waiting for wake word")

            # Non-blocking input check + wake word in parallel
            import select
            import sys

            wake_detected = False
            typed_question = None

            # Listen for wake word with short timeout chunks
            # Also check for typed input
            audio_buffer = []
            import sounddevice as sd
            import numpy as np

            def audio_cb(indata, frames, t, status):
                audio_buffer.append(indata.copy())

            with sd.InputStream(samplerate=16000, channels=1,
                                dtype='int16', blocksize=1280,
                                callback=audio_cb):
                print("[MAIN] Listening for 'Hey Jarvis' or type your question...")
                start = time.time()
                while time.time() - start < 60:  # listen for 60 seconds
                    # Check for typed input
                    if select.select([sys.stdin], [], [], 0)[0]:
                        typed_question = sys.stdin.readline().strip()
                        if typed_question:
                            wake_detected = True
                            break

                    # Check wake word
                    if audio_buffer:
                        chunk = audio_buffer.pop(0)
                        pred = wake_model.predict(chunk.flatten())
                        for model_name, score in pred.items():
                            if score >= 0.4:
                                print(f"[MAIN] Wake word detected! Score: {score:.2f}")
                                wake_detected = True
                                break
                    if wake_detected:
                        break
                    time.sleep(0.01)

            if not wake_detected:
                continue

            # ── LISTEN — get question ─────────────────────
            if typed_question:
                question = typed_question
                print(f"[MAIN] Question (typed): {question}")
            else:
                speak("Cheppandi!", language)
                print("[MAIN] Listening for your question...")
                question = listen_and_transcribe("english", timeout=8)

                if not question:
                    speak("Meeru emi cheppaledu. Malli try cheyyandi!", language)
                    continue

                print(f"[MAIN] You said: {question}")

            # ── THINK ────────────────────────────────────
            print("[MAIN] Thinking...")
            response = ask_chintu(question, age, language)

            if not response:
                response = "Adhi manchhi prashna! Naku inka nerchukovaalanidi undhi!"

            # ── SPEAK ────────────────────────────────────
            speak(response, language)

        except KeyboardInterrupt:
            print("\n[MAIN] Stopping Chintu...")
            speak("Bye bye!", language)
            break

        except Exception as e:
            print(f"[MAIN] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run()