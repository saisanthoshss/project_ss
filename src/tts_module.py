import asyncio
import edge_tts
import pygame
import os
import json

# ── CONFIG ──────────────────────────────────────────────
CACHE_DIR = "/mnt/d/project_ss/tts_cache"
PROFILE_PATH = "/mnt/d/project_ss/child_profile.json"

# Telugu and English voice names from Microsoft Neural TTS
VOICES = {
    "telugu": "te-IN-MohanNeural",
    "english": "en-IN-NeerjaNeural"
}

# ── LOAD CHILD PROFILE ───────────────────────────────────
def load_profile():
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

# ── GENERATE AUDIO FILE ──────────────────────────────────
async def generate_audio(text, language="telugu"):
    """Convert text to speech and save as mp3 file"""
    voice = VOICES.get(language, VOICES["telugu"])
    
    # Create a safe filename from the text
    safe_name = "".join(c for c in text if c.isalnum() or c == " ")
    safe_name = safe_name[:40].strip().replace(" ", "_")
    filename = f"{CACHE_DIR}/{language}_{safe_name}.mp3"
    
    # If already cached, skip generation
    if os.path.exists(filename):
        return filename
    
    # Generate using edge-tts
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(filename)
    return filename

# ── PLAY AUDIO FILE ──────────────────────────────────────
def play_audio(filepath):
    """Play an mp3 audio file through speakers"""
    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

# ── MAIN SPEAK FUNCTION ──────────────────────────────────
def speak(text, language=None):
    """
    Main function — converts text to speech and plays it.
    Usage: speak("Namaskaram", "telugu")
    """
    if language is None:
        profile = load_profile()
        language = profile.get("language", "telugu")
    
    print(f"[TTS] Speaking ({language}): {text}")
    
    filepath = asyncio.run(generate_audio(text, language))
    play_audio(filepath)

# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing TTS module...")
    
    # Test Telugu
    speak("Namaskaram, nenu Chintu. Meeru ela unnaru?", "telugu")
    
    # Test English  
    speak("Hello! I am Chintu. How are you?", "english")
    
    print("TTS test complete!")