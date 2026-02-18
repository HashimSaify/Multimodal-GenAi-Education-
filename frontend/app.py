import base64
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Multimodal GenAI Education", layout="wide")

st.markdown(
    """
<style>
.hero {
    background: linear-gradient(135deg, #f5f7ff 0%, #eef9f1 100%);
    border: 1px solid #dbe3ff;
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 16px;
}
.hero h1 { margin: 0 0 6px 0; font-size: 28px; }
.hero p { margin: 0; color: #334155; }
.section-title { margin-top: 14px; }
</style>
<div class="hero">
  <h1>Multimodal Generative AI for Education</h1>
  <p>Enter a topic, get explanations, flashcards, diagrams, and similar concepts.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Input")
    topic = st.text_input("Enter a concept", "Explain Transformer architecture in NLP")
    grade = st.selectbox("Grade Level", ["", "School", "College", "Professional"])
    generate_btn = st.button("Generate")

if generate_btn:
    with st.spinner("Generating content..."):
        content_res = requests.post(
            f"{API_URL}/generate-content",
            json={"topic": topic, "grade_level": grade if grade else None},
        )
        if content_res.status_code != 200:
            st.error(content_res.text)
            st.stop()
        content = content_res.json()

    with st.spinner("Generating images..."):
        image_res = requests.post(
            f"{API_URL}/generate-image",
            json={"topic": topic, "grade_level": grade if grade else None},
        )
        if image_res.status_code != 200:
            st.error(image_res.text)
            st.stop()
        images = image_res.json()

    with st.spinner("Storing vectors..."):
        requests.post(
            f"{API_URL}/store-vector",
            json={"prompt": topic, "explanation": content.get("overview")},
        )

    st.subheader("Concept Overview")
    st.write(content.get("overview"))

    st.subheader("Key Points")
    st.markdown("\n".join([f"- {p}" for p in content.get("key_points", [])]))

    st.subheader("Real-world Example")
    st.write(content.get("real_world_example"))

    st.subheader("Flashcards")
    for fc in content.get("flashcards", []):
        st.info(fc)

    st.subheader("Summary")
    st.write(content.get("summary"))

    st.subheader("Images")
    col1, col2 = st.columns(2)
    with col1:
        if images.get("diagram_b64"):
            st.image(base64.b64decode(images["diagram_b64"]), caption="Concept Diagram")
    with col2:
        if images.get("flashcard_b64"):
            st.image(base64.b64decode(images["flashcard_b64"]), caption="Flashcard Visual")

    st.subheader("Similar Concepts")
    search_res = requests.post(
        f"{API_URL}/search",
        json={"query": topic, "top_k": 3},
    )
    if search_res.status_code == 200:
        results = search_res.json().get("results", [])
        for r in results:
            st.write(f"**Prompt:** {r['prompt']}")
            st.write(r["explanation"])
