import json
import os
from llama_cpp import Llama

# ── CONFIG ──────────────────────────────────────────────
MODEL_PATH   = "/mnt/d/project_ss/models/phi2/phi-2.Q4_K_M.gguf"
PROFILE_PATH = "/mnt/d/project_ss/child_profile.json"

# ── LOAD PROFILE ─────────────────────────────────────────
def load_profile():
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

# ── SYSTEM PROMPT ────────────────────────────────────────
def build_system_prompt(age, language):
    """Build age and language appropriate system prompt"""

    age_guidance = {
        1: "Use only single words or very short 2-word phrases. Only animal sounds and simple words.",
        2: "Use very simple 3-4 word sentences. Simple words only. Be very gentle and slow.",
        3: "Use simple short sentences. 5-6 words maximum. Warm and encouraging tone.",
        4: "Use clear simple sentences. Can explain basic concepts in 1-2 sentences.",
        5: "Use clear sentences. Can give slightly longer explanations. Encourage curiosity."
    }

    lang_instruction = {
        "telugu": "Always respond in Telugu language. Use simple Telugu words a child can understand.",
        "english": "Always respond in English. Use simple words a child can understand."
    }

    guidance = age_guidance.get(age, age_guidance[3])
    lang     = lang_instruction.get(language, lang_instruction["telugu"])

    prompt = f"""You are Chintu, a friendly and warm AI companion toy for children aged {age}.
{lang}
{guidance}

You only talk about these safe topics:
- Colors (rengu / colours)
- Animals (jeevalu / animals) and their sounds
- Numbers (sankhyalu / numbers) 1 to 20
- Body parts (shareera bhagalu / body parts)
- Shapes (akrutulu / shapes)
- Greetings and manners (namaskaram, please, thank you)
- Simple stories and rhymes
- Indian festivals and culture
- Mantras (Om, simple prayers)

Rules you must always follow:
- Never discuss violence, adult topics, or anything harmful
- If asked about something outside your topics, gently say you don't know and suggest a fun topic
- Always be warm, encouraging, and patient
- Keep responses very short — maximum 2 sentences
- Never say anything scary or sad

You are a best friend to this child. Be playful and loving."""

    return prompt

# ── LOAD MODEL ───────────────────────────────────────────
_llm = None

def load_model():
    """Load LLM model once and keep in memory"""
    global _llm
    if _llm is None:
        print("[LLM] Loading Phi-2 model... please wait")
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,
            n_threads=4,
            verbose=False
        )
        print("[LLM] Model ready")
    return _llm

# ── ASK CHINTU ───────────────────────────────────────────
def ask_chintu(question, age=3, language="telugu"):
    """
    Send question to LLM and get Chintu's response.
    Usage: response = ask_chintu("What sound does a cow make?", age=3, language="telugu")
    """
    llm = load_model()
    system = build_system_prompt(age, language)

    full_prompt = f"{system}\n\nChild asks: {question}\nChintu responds:"

    print(f"[LLM] Thinking...")
    response = llm(
        full_prompt,
        max_tokens=80,
        stop=["Child asks:", "\n\n", "Human:", "User:"],
        echo=False
    )

    answer = response["choices"][0]["text"].strip()
    print(f"[LLM] Response: {answer}")
    return answer

# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing LLM module...")

    profile = load_profile()
    age      = profile.get("age", 3)
    language = profile.get("language", "telugu")

    print(f"Child age: {age}, Language: {language}")
    print()

    test_questions = [
        "What sound does a cow make?",
        "What colour is the sky?",
        "How many fingers do I have?",
    ]

    for q in test_questions:
        print(f"Question: {q}")
        answer = ask_chintu(q, age, language)
        print(f"Chintu: {answer}")
        print()

    print("LLM test complete!")