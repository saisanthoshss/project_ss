import json
import os

# ── CONFIG ──────────────────────────────────────────────
CONTENT_DIR = "/mnt/d/project_ss/content"

# ── LOAD JSON FILES ──────────────────────────────────────
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# ── CONTENT LOADERS ──────────────────────────────────────
def get_colours():
    return load_json(f"{CONTENT_DIR}/colours/colours.json")["colours"]
def get_english_alphabets():
    return load_json(f"{CONTENT_DIR}/alphabets/english_alphabets.json")["english_alphabets"]

def get_telugu_vowels():
    return load_json(f"{CONTENT_DIR}/alphabets/telugu_alphabets.json")["telugu_vowels"]

def get_telugu_consonants():
    return load_json(f"{CONTENT_DIR}/alphabets/telugu_alphabets.json")["telugu_consonants"]

def get_greetings():
    return load_json(f"{CONTENT_DIR}/greetings/greetings.json")["greetings"]

def get_mantras():
    return load_json(f"{CONTENT_DIR}/mantras/mantras.json")["mantras"]
def get_animals():
    return load_json(f"{CONTENT_DIR}/animals/animals.json")["animals"]

def get_numbers():
    return load_json(f"{CONTENT_DIR}/numbers/numbers.json")["numbers"]

def get_body_parts():
    return load_json(f"{CONTENT_DIR}/alphabets/body_parts.json")["body_parts"]

# ── SEARCH FUNCTIONS ─────────────────────────────────────
def find_colour(query):
    """Find colour by English or Telugu name"""
    query = query.lower()
    for c in get_colours():
        if query in c["english"].lower() or query in c["telugu"].lower():
            return c
    return None

def find_animal(query):
    """Find animal by English or Telugu name"""
    query = query.lower()
    for a in get_animals():
        if query in a["english"].lower() or query in a["telugu"].lower():
            return a
    return None

def find_number(query):
    """Find number by digit or word"""
    query = query.lower().strip()
    for n in get_numbers():
        if (query == str(n["digit"]) or
            query in n["english"].lower() or
            query in n["telugu"].lower()):
            return n
    return None

def find_body_part(query):
    """Find body part by English or Telugu name"""
    query = query.lower()
    for b in get_body_parts():
        if query in b["english"].lower() or query in b["telugu"].lower():
            return b
    return None
def find_alphabet_english(query):
    """Find English alphabet by letter"""
    query = query.upper().strip()
    for a in get_english_alphabets():
        if a["letter"] == query:
            return a
    return None

def find_alphabet_telugu(query):
    """Find Telugu alphabet by romanized form"""
    query = query.lower().strip()
    for v in get_telugu_vowels():
        if query == v["romanized"] or query in v["word"].lower():
            return v
    for c in get_telugu_consonants():
        if query == c["romanized"] or query in c["word"].lower():
            return c
    return None

def find_greeting(query):
    """Find greeting by English or Telugu word"""
    query = query.lower()
    for g in get_greetings():
        if query in g["english"].lower() or query in g["telugu"].lower():
            return g
    return None

def find_mantra(query):
    """Find mantra by name"""
    query = query.lower()
    for m in get_mantras():
        if query in m["name"].lower() or query in m["telugu_name"].lower():
            return m
    return None

# ── DETECT TOPIC ─────────────────────────────────────────
def detect_topic(question):
    """
    Detect what topic the question is about.
    Returns (topic, data) tuple.
    """
    q = question.lower()

    # Check for colour keywords
    colour_words = ["colour", "color", "rengu", "red", "blue", "green",
                    "yellow", "white", "black", "pink", "orange", "purple",
                    "erra", "neela", "pachi", "peetha", "tella", "nalla"]
    for word in colour_words:
        if word in q:
            # Try to find specific colour
            for c in get_colours():
                if c["english"] in q or c["telugu"] in q:
                    return "colour_specific", c
            return "colour_general", get_colours()

    # Check for animal keywords
    animal_words = ["animal", "jeevula", "sound", "antundi",
                    "cow", "dog", "cat", "lion", "tiger", "elephant",
                    "aavu", "kukka", "pilli", "simham", "puli", "enugu"]
    for word in animal_words:
        if word in q:
            for a in get_animals():
                if a["english"] in q or a["telugu"] in q:
                    return "animal_specific", a
            return "animal_general", get_animals()
# Special case: body part count questions — must check BEFORE numbers
    if "how many finger" in q or "fingers" in q:
        for b in get_body_parts():
            if b["english"] == "fingers":
                return "body_specific", b
    if "how many eye" in q or "eyes" in q:
        for b in get_body_parts():
            if b["english"] == "eyes":
                return "body_specific", b
    if "how many ear" in q or "ears" in q:
        for b in get_body_parts():
            if b["english"] == "ears":
                return "body_specific", b
    # Check for number keywords
    # Check for number keywords
    number_words = ["number", "count", "how many", "enni", "sankhya",
                    "one", "two", "three", "four", "five"]
    for word in number_words:
        if word in q:
            for n in get_numbers():
                if n["english"] in q or n["telugu"] in q:
                    return "number_specific", n
            return "number_general", get_numbers()[:5]
# Special case: how many fingers/eyes/ears
    if "how many finger" in q or "fingers" in q:
        for b in get_body_parts():
            if b["english"] == "fingers":
                return "body_specific", b
    if "how many eye" in q or "eyes" in q:
        for b in get_body_parts():
            if b["english"] == "eyes":
                return "body_specific", b
    if "how many ear" in q or "ears" in q:
        for b in get_body_parts():
            if b["english"] == "ears":
                return "body_specific", b
    # Check for body part keywords
    body_words = ["body", "shareera", "head", "eyes", "ears", "nose",
                  "mouth", "hands", "fingers", "legs", "tala", "kallu",
                  "chevulu", "mukkhu", "nooru", "chethulu", "kaalu",
                  "how many fingers", "finger", "how many eyes", "how many ears"]
    for word in body_words:
        if word in q:
            for b in get_body_parts():
                if b["english"] in q or b["telugu"] in q:
                    return "body_specific", b
            return "body_general", get_body_parts()
    # Check for alphabet keywords
    alpha_words = ["alphabet", "letter", "aksharam", "aksharalu",
                   "telugu letter", "english letter", "a for", "b for"]
    for word in alpha_words:
        if word in q:
            # Check for specific letter
            for letter in "abcdefghijklmnopqrstuvwxyz":
                if f" {letter} " in f" {q} " or q.startswith(f"{letter} ") or q.endswith(f" {letter}"):
                    result = find_alphabet_english(letter.upper())
                    if result:
                        return "alphabet_english", result
            return "alphabet_general", get_english_alphabets()[:5]

    # Check for greeting keywords
    # Check for greeting keywords — check BEFORE animals
    greeting_words = ["thank you", "thank", "namaskaram", "dhanyavaadalu",
                      "please", "dayachesi", "sorry", "kshaminchaandi",
                      "good morning", "good night", "subhodayam",
                      "how do you say hello", "how do you say thank",
                      "how do you say please", "how do you say sorry"]
    for word in greeting_words:
        if word in q:
            result = find_greeting(word.split()[0] if len(word.split()) > 1 else word)
            if result:
                return "greeting_specific", result
            return "greeting_general", get_greetings()
    for word in greeting_words:
        if word in q:
            result = find_greeting(word)
            if result:
                return "greeting_specific", result
            return "greeting_general", get_greetings()

    # Check for mantra keywords
    # Special case for Om
    if "om mantra" in q or "tell me about om" in q or q.strip() == "om":
        result = find_mantra("om")
        if result:
            return "mantra_specific", result

    mantra_words = ["mantra", "prayer", "gayatri", "saraswati",
                    "shiva", "namah", "lullaby", "laali", "puja",
                    "om namah", "tell me about om", "what is om"]
    # Special case for Om alone
    if q.strip() in ["om", "tell me about om", "what is om mantra", "om mantra"]:
        result = find_mantra("om")
        if result:
            return "mantra_specific", result
    for word in mantra_words:
        if word in q:
            result = find_mantra(word)
            if result:
                return "mantra_specific", result
            return "mantra_general", get_mantras()
    return "unknown", None

# ── BUILD CONTEXT FOR LLM ────────────────────────────────
def get_context(question, language="telugu"):
    """
    Get relevant content context for LLM based on question.
    Returns a context string to include in LLM prompt.
    """
    topic, data = detect_topic(question)

    if topic == "colour_specific":
        if language == "telugu":
            return f"FACT: {data['english']} colour is called '{data['telugu']}' in Telugu. Example: {data['example_telugu']}"
        else:
            return f"FACT: {data['english']} colour is called '{data['telugu']}' in Telugu. Example: {data['example_english']}"

    elif topic == "colour_general":
        colours_str = ", ".join([f"{c['english']}={c['telugu']}" for c in data[:6]])
        return f"FACT: Some colours in Telugu: {colours_str}"

    elif topic == "animal_specific":
        if language == "telugu":
            return f"FACT: {data['english']} is called '{data['telugu']}' in Telugu. Sound: '{data['sound_telugu']}'. {data['fun_fact_telugu']}"
        else:
            return f"FACT: {data['english']} is called '{data['telugu']}' in Telugu. Sound: '{data['sound_english']}'. {data['fun_fact_english']}"

    elif topic == "animal_general":
        animals_str = ", ".join([f"{a['english']}={a['telugu']}" for a in data[:5]])
        return f"FACT: Some animals in Telugu: {animals_str}"

    elif topic == "number_specific":
        return f"FACT: Number {data['digit']} is '{data['english']}' in English and '{data['telugu']}' in Telugu."

    elif topic == "number_general":
        nums_str = ", ".join([f"{n['digit']}={n['telugu']}" for n in data])
        return f"FACT: Numbers in Telugu: {nums_str}"

    elif topic == "body_specific":
        if language == "telugu":
            return f"FACT: {data['english']} is called '{data['telugu']}' in Telugu. {data.get('function_telugu', '')}"
        else:
            return f"FACT: {data['english']} is called '{data['telugu']}' in Telugu. {data.get('function_english', '')}"

    elif topic == "body_general":
        parts_str = ", ".join([f"{b['english']}={b['telugu']}" for b in data[:5]])
        return f"FACT: Body parts in Telugu: {parts_str}"
    elif topic == "alphabet_english" and data:
        return f"FACT: Letter {data['letter']} is for {data['word_english']}. In Telugu: {data['word_telugu']}"

    elif topic == "alphabet_general":
        return "FACT: English alphabets go from A to Z. A for Apple, B for Ball, C for Cat!"

    elif topic == "greeting_specific" and data:
        if language == "telugu":
            return f"FACT: '{data['english']}' ni Telugu lo '{data['telugu']}' antaaru. {data['when_to_use_telugu']}."
        else:
            return f"FACT: '{data['english']}' in Telugu is '{data['telugu']}'. Use it: {data['when_to_use']}."

    elif topic == "mantra_specific" and data:
        first_line = data['lines'][0]
        if language == "telugu":
            return f"FACT: {data['name']} mantramu: '{first_line['text']}'. Artham: {first_line['meaning_telugu']}. {data['significance_telugu']}"
        else:
            return f"FACT: {data['name']} mantra: '{first_line['text']}'. Meaning: {first_line['meaning_english']}. {data['significance_english']}"

    elif topic == "mantra_general":
        return "FACT: Important mantras are Om, Om Namah Shivaya, Gayatri Mantra, and Saraswati Vandana."
    return ""

# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing content engine...")
    print()

    test_questions = [
        "What sound does a cow make?",
        "What colour is red in Telugu?",
        "How many fingers do I have?",
        "What is letter A for?",
        "How do you say thank you in Telugu?",
        "Tell me about Om mantra",
        "What is Saraswati Vandana?",
    ]
    

    for q in test_questions:
        context = get_context(q, "telugu")
        print(f"Q: {q}")
        print(f"Context: {context}")
        print()

    print("Content engine test complete!")