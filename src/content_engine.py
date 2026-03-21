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
    animal_words = ["animal", "jeevula", "sound", "say", "antundi",
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

    return ""

# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing content engine...")
    print()

    test_questions = [
        "What sound does a cow make?",
        "What colour is the sky?",
        "How many fingers do I have?",
        "What is lion called in Telugu?",
        "What colour is red in Telugu?",
    ]

    for q in test_questions:
        context = get_context(q, "telugu")
        print(f"Q: {q}")
        print(f"Context: {context}")
        print()

    print("Content engine test complete!")