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
        1: "Respond with only 1-2 simple words. Only animal sounds and basic words like 'yes' or 'no'.",
        2: "Respond in exactly 1 short sentence of 4-5 words maximum. Very simple words only.",
        3: "Respond in exactly 1 sentence. Maximum 8 words. Simple and clear.",
        4: "Respond in 1-2 short sentences. Maximum 15 words total. Simple explanations.",
        5: "Respond in 1-2 sentences. Maximum 20 words total. Can give simple reasons."
    }

    lang_instruction = {
        "telugu": "You MUST respond only in Telugu language. Use simple Telugu words.",
        "english": "You MUST respond only in English. Use simple words a child understands."
    }

    guidance = age_guidance.get(age, age_guidance[3])
    lang     = lang_instruction.get(language, lang_instruction["telugu"])

    prompt = f"""You are Chintu, a friendly toy for children aged {age} years.
{lang}
{guidance}

FACTS YOU MUST KNOW:
- A cow says: Amba (Telugu) / Moo (English)
- A dog says: Bau bau (Telugu) / Woof (English)  
- A cat says: Meow
- A lion says: Garjana (Telugu) / Roar (English)
- Sky colour: Neela (Telugu) / Blue (English)
- Grass colour: Pachi (Telugu) / Green (English)
- Sun colour: Peetha (Telugu) / Yellow (English)
- Humans have: 5 fingers on each hand, 10 fingers total
- Humans have: 2 eyes, 2 ears, 1 nose, 1 mouth

ALLOWED TOPICS ONLY:
- Animal names and sounds
- Colors (rengu)
- Numbers 1-20
- Body parts
- Basic shapes
- Greetings
- Short stories
- Mantras and prayers

RULES:
- NEVER give more than 2 sentences
- NEVER use bullet points or lists
- NEVER discuss violence, adult content, or scary things
- If asked something outside allowed topics, say: "Naku telidhu, mana jeevula gurinchi mataladamu!" (in Telugu)
- Always be warm and encouraging
- End response immediately after 1-2 sentences"""

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
    Smart response system:
    - Known topics (colours, animals, numbers, body parts) -> direct answer from content
    - Unknown topics -> LLM generates response
    """
    import sys
    sys.path.insert(0, "/mnt/d/project_ss/src")
    from content_engine import detect_topic, get_context

    # Detect topic first
    topic, data = detect_topic(question)

    # ── DIRECT ANSWERS from content library ──────────────
    if topic == "animal_specific" and data:
        if language == "telugu":
            if "sound" in question.lower() or "antundi" in question.lower() or "say" in question.lower():
                return f"{data['telugu']} '{data['sound_telugu']}' antundi! {data['fun_fact_telugu']}"
            else:
                return f"{data['english']} ni Telugu lo '{data['telugu']}' antaru. {data['fun_fact_telugu']}"
        else:
            if "sound" in question.lower() or "say" in question.lower():
                return f"A {data['english']} says {data['sound_english']}! {data['fun_fact_english']}"
            else:
                return f"{data['english']} is called '{data['telugu']}' in Telugu. {data['fun_fact_english']}"

    elif topic == "colour_specific" and data:
        if language == "telugu":
            return f"{data['english']} rengu Telugu lo '{data['telugu']}' antaru. {data['example_telugu']}!"
        else:
            return f"{data['english']} colour is called '{data['telugu']}' in Telugu. {data['example_english']}!"

    elif topic == "colour_general":
        if language == "telugu":
            return "Chala rengulu unnaayi! Erra, neela, pachi, peetha - anni rengulu manchhivi!"
        else:
            return "There are many colours! Red, blue, green, yellow - all colours are beautiful!"

    elif topic == "number_specific" and data:
        if language == "telugu":
            return f"{data['digit']} ni Telugu lo '{data['telugu']}' antaru!"
        else:
            return f"{data['digit']} is called '{data['telugu']}' in Telugu!"

    elif topic == "body_specific" and data:
        if language == "telugu":
            return f"{data['english']} ni Telugu lo '{data['telugu']}' antaru. {data.get('function_telugu', '')}!"
        else:
            return f"{data['english']} is called '{data['telugu']}' in Telugu. {data.get('function_english', '')}!"

    elif topic == "body_general":
        if language == "telugu":
            return "Mana shareeram lo tala, kallu, chevulu, mukkhu, nooru, chethulu, kaalu untaayi!"
        else:
            return "Our body has head, eyes, ears, nose, mouth, hands and legs!"

    # ── LLM for unknown topics ────────────────────────────
    llm    = load_model()
    system = build_system_prompt(age, language)
    context = get_context(question, language)

    if context:
        full_prompt = f"{system}\n\n{context}\n\nChild asks: {question}\nChintu responds (1 sentence only):"
    else:
        full_prompt = f"{system}\n\nChild asks: {question}\nChintu responds (1 sentence only):"

    print(f"[LLM] Using AI for unknown topic...")
    response = llm(
        full_prompt,
        max_tokens=50,
        stop=["Child asks:", "\n\n", "Human:", "User:"],
        echo=False
    )

    answer = response["choices"][0]["text"].strip()
    answer = answer.replace("Chintu:", "").replace("Answer:", "").strip()

    if not answer:
        if language == "telugu":
            return "Adhi chala manchhi prashna! Naku inka nerchukovaalanidi undhi!"
        else:
            return "That is a great question! I am still learning about that!"

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
        "What is elephant called in Telugu?",
        "What colour is red called in Telugu?",
    ]

    for q in test_questions:
        print(f"Question: {q}")
        answer = ask_chintu(q, age, language)
        print(f"Chintu: {answer}")
        print()

    print("LLM test complete!")