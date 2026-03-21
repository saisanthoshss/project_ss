import vosk
import sounddevice as sd
import queue
import json
import time
import os

# ── CONFIG ──────────────────────────────────────────────
MODELS = {
    "telugu": "/mnt/d/project_ss/models/telugu/vosk-model-small-te-0.42",
    "english": "/mnt/d/project_ss/models/english/vosk-model-small-en-us-0.15"
}

SAMPLE_RATE = 16000
BLOCK_SIZE  = 8000

# ── LOAD MODEL ───────────────────────────────────────────
_loaded_models = {}

def get_model(language="telugu"):
    """Load and cache model so it is not reloaded every time"""
    if language not in _loaded_models:
        model_path = MODELS.get(language, MODELS["telugu"])
        print(f"[STT] Loading {language} model...")
        _loaded_models[language] = vosk.Model(model_path)
        print(f"[STT] {language} model ready")
    return _loaded_models[language]

# ── LISTEN AND TRANSCRIBE ────────────────────────────────
def listen_and_transcribe(language="telugu", timeout=8):
    """
    Listen from microphone and convert speech to text.
    Returns transcribed text string.
    Usage: text = listen_and_transcribe("telugu", timeout=8)
    """
    model = get_model(language)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        audio_queue.put(bytes(indata))

    print(f"[STT] Listening ({language}) for {timeout} seconds...")
    result_text = ""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result.get("text"):
                    result_text += result["text"] + " "

        # Get any remaining words
        final = json.loads(recognizer.FinalResult())
        if final.get("text"):
            result_text += final["text"]

    result_text = result_text.strip()
    print(f"[STT] Heard: '{result_text}'")
    return result_text

# ── DETECT LANGUAGE ──────────────────────────────────────
def detect_and_transcribe(timeout=8):
    """
    Try Telugu first, fall back to English.
    Returns (text, language) tuple.
    """
    # Try Telugu first
    text = listen_and_transcribe("telugu", timeout)
    if text:
        return text, "telugu"
    
    # If nothing heard in Telugu, try English
    text = listen_and_transcribe("english", timeout)
    if text:
        return text, "english"
    
    return "", "telugu"

# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing STT module...")
    print("Speak something in English when ready...")
    time.sleep(1)
    
    text = listen_and_transcribe("english", timeout=6)
    
    if text:
        print(f"SUCCESS: Heard -> '{text}'")
    else:
        print("Nothing heard. Check microphone.")
    
    print("STT test complete!")