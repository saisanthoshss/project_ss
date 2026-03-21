import time
import json
import os
import sys
import threading

sys.path.insert(0, "/mnt/d/project_ss/src")

from tts_module import speak
from stt_module import listen_and_transcribe
from llm_module import ask_chintu, load_model

# ── CONFIG ──────────────────────────────────────────────
PROFILE_PATH = "/mnt/d/project_ss/child_profile.json"

STATE_SLEEP  = "SLEEP"
STATE_LISTEN = "LISTEN"
STATE_THINK  = "THINK"
STATE_SPEAK  = "SPEAK"

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

    print("[MAIN] Loading AI brain...")
    load_model()

    print("[MAIN] Chintu is ready!")
    speak("Namaskaram! Nenu Chintu. Meeru ela unnaru?", language)

    print("\n[MAIN] Commands:")
    print("  Press ENTER -> speak your question (voice mode)")
    print("  Type your question and press ENTER -> text mode")
    print("  Type 'quit' -> stop Chintu\n")

    while True:
        try:
            user_input = input("[MAIN] Press ENTER to speak OR type question: ").strip()

            if user_input.lower() == "quit":
                speak("Bye bye!", language)
                break

            # ── TEXT MODE ────────────────────────────────
            if user_input:
                question = user_input
                print(f"[MAIN] Question (typed): {question}")

            # ── VOICE MODE ───────────────────────────────
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