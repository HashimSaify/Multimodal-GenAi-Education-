def _infer_subject(topic: str) -> str:
    t = topic.lower()
    if any(k in t for k in ["physics", "force", "energy", "motion", "optics"]):
        return "physics"
    if any(k in t for k in ["biology", "cell", "photosynthesis", "dna", "evolution"]):
        return "biology"
    if any(k in t for k in ["chemistry", "molecule", "reaction", "acid", "base"]):
        return "chemistry"
    if any(k in t for k in ["algorithm", "data", "neural", "transformer", "nlp", "computer"]):
        return "computer science"
    if any(k in t for k in ["math", "algebra", "calculus", "geometry", "probability"]):
        return "mathematics"
    return "general education"


def build_validation_prompt(topic: str) -> str:
    return f"""
Classify the following topic.
Topic: "{topic}"

Is this topic a formal academic subject, scientific concept, or complex professional skill?
(Examples of scientific/academic: Photosynthesis, Quantum Mechanics, World War II, Machine Learning, Python Programming).

If the topic is everyday casual advice, a cooking recipe, food, celebrity gossip, or basic instructions (e.g., "how to make maggi", "best movies", "how to tie a shoe"), answer with NO.
If it is academic/scientific, answer with YES.

Respond with EXACTLY ONE WORD: YES or NO.
""".strip()

def build_prompt(topic: str, grade_level: str | None):
    grade_text = f" for {grade_level} students" if grade_level else ""
    subject = _infer_subject(topic)
    return f"""
You are an expert education assistant.

Your task is to explain the topic "{topic}"{grade_text}.
Adjust depth and vocabulary for {grade_level or 'a general audience'}.
Focus on clear structure and accuracy for {subject}.

Return ONLY valid JSON with EXACTLY these fields:
{{
  "overview": "string",
  "key_points": ["string", "string"],
  "real_world_example": "string",
  "flashcards": ["string", "string"],
  "summary": "string"
}}
""".strip()
