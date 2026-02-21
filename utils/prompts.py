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


def build_prompt(topic: str, grade_level: str | None):
    grade_text = f" for {grade_level} students" if grade_level else ""
    subject = _infer_subject(topic)
    return f"""
You are an expert education assistant. First, determine if the topic "{topic}" is related to education, academia, learning concepts, or skills.
If the topic is clearly NOT related to education (e.g. general chit-chat, cooking recipes, inappropriate content):
Return ONLY valid JSON with a single field:
- error: "This topic does not appear to be related to education. Please ask about an academic subject, concept, or skill."

If the topic IS related to education:
Explain the topic: {topic}{grade_text}.
Adjust depth and vocabulary for {grade_level or 'a general audience'}.
Focus on clear structure and accuracy for {subject} topics.
Return ONLY valid JSON with the following fields:
- overview (string)
- key_points (array of strings)
- real_world_example (string)
- flashcards (array of 3-5 short strings)
- summary (string)
""".strip()
