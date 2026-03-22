import openwakeword
from openwakeword.model import Model
import sounddevice as sd
import numpy as np
import time
import os

# ── CONFIG ──────────────────────────────────────────────
SAMPLE_RATE  = 16000
CHUNK_SIZE   = 1280  # 80ms chunks — required by openWakeWord
THRESHOLD    = 0.4   # confidence threshold 0-1

# Pre-trained model path — change to custom Chintu model later
PRETRAINED_MODEL = "/mnt/d/project_ss/venv/lib/python3.11/site-packages/openwakeword/resources/models/hey_jarvis_v0.1.tflite"

# Custom Chintu model path — will be created after training
CUSTOM_MODEL = "/mnt/d/project_ss/models/wakeword/chintu.tflite"

# ── LOAD MODEL ───────────────────────────────────────────
def load_wake_word_model(use_custom=False):
    """Load wake word model"""
    if use_custom and os.path.exists(CUSTOM_MODEL):
        print("[WAKE] Loading custom Chintu wake word model...")
        model = Model(wakeword_models=[CUSTOM_MODEL])
        print("[WAKE] Custom Chintu model ready")
    else:
        print("[WAKE] Loading pre-trained 'hey jarvis' model for testing...")
        model = Model(wakeword_models=["hey_jarvis_v0.1"])
        print("[WAKE] Pre-trained model ready")
    return model

# ── LISTEN FOR WAKE WORD ─────────────────────────────────
def wait_for_wake_word(model=None, use_custom=False, timeout=None):
    """
    Listen continuously until wake word is detected.
    Returns True when wake word heard.
    timeout: seconds to listen before giving up (None = listen forever)
    """
    if model is None:
        model = load_wake_word_model(use_custom)

    print("[WAKE] Listening for wake word...")
    audio_buffer = []
    detected = False
    start_time = time.time()

    def audio_callback(indata, frames, time_info, status):
        audio_buffer.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE,
        callback=audio_callback
    ):
        while not detected:
            # Check timeout
            if timeout and time.time() - start_time > timeout:
                print("[WAKE] Timeout — no wake word detected")
                return False

            # Process available audio chunks
            if audio_buffer:
                chunk = audio_buffer.pop(0)
                audio_flat = chunk.flatten()

                # Run wake word detection
                prediction = model.predict(audio_flat)

                # Check all models for detection
                for model_name, score in prediction.items():
                    if score >= THRESHOLD:
                        print(f"[WAKE] Wake word detected! Model: {model_name}, Score: {score:.2f}")
                        return True
            else:
                time.sleep(0.01)

    return False

# ── QUICK DETECT (one shot) ──────────────────────────────
def quick_detect(audio_chunk, model):
    """
    Check a single audio chunk for wake word.
    Returns (detected, score) tuple.
    Use this when integrating into main loop.
    """
    audio_flat = np.array(audio_chunk).flatten()
    prediction = model.predict(audio_flat)

    for model_name, score in prediction.items():
        if score >= THRESHOLD:
            return True, score
    return False, 0.0

# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Wake word module test")
    print("Using pre-trained 'hey jarvis' model")
    print("Say 'Hey Jarvis' clearly to test detection")
    print("Press Ctrl+C to stop")
    print()

    model = load_wake_word_model(use_custom=False)

    print("Listening... say 'Hey Jarvis'")
    detected = wait_for_wake_word(model=model, timeout=30)

    if detected:
        print("SUCCESS! Wake word system is working!")
        print("Next step: train custom 'Chintu' model")
    else:
        print("No wake word detected in 30 seconds")
        print("Check microphone and try again")