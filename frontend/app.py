import base64
import streamlit as st
import requests
import time
import uuid
from datetime import datetime, date, timedelta

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="EduGen AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Initialize session state
defaults = {
    "sessions": {},
    "current_session_id": None,
    "grade_level": "Professional",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Convert legacy history format gracefully
if "history" in st.session_state and not st.session_state.sessions:
    for h in st.session_state.history:
        sid = str(uuid.uuid4())
        st.session_state.sessions[sid] = {
            "id": sid,
            "title": h.get("topic", "Untitled"),
            "timestamp": h.get("timestamp", time.time()),
            "turns": [
                {
                    "topic": h.get("topic"),
                    "grade": h.get("grade"),
                    "content": h.get("content", {}),
                    "images": h.get("images", {}),
                    "timestamp": h.get("timestamp", time.time())
                }
            ]
        }

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary:      #0a0a0f;
        --bg-secondary:    #131318;
        --bg-tertiary:     #1a1a22;
        --sidebar-bg:      #0f0f14;
        --surface:         #1e1e28;
        --surface-hover:   #252532;
        --border:          #2a2a38;
        --border-subtle:   #1e1e28;
        --text-primary:    #f0f0f5;
        --text-secondary:  #a8a8b8;
        --text-muted:      #6e6e7e;
        --accent:          #6366f1;
        --accent-hover:    #7c7ff5;
        --accent-glow:     rgba(99, 102, 241, 0.25);
        --success:         #10b981;
        --warning:         #f59e0b;
        --radius-sm:       6px;
        --radius-md:       10px;
        --radius-lg:       14px;
        --shadow-sm:       0 2px 8px rgba(0,0,0,0.3);
        --shadow-md:       0 4px 16px rgba(0,0,0,0.4);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    html, body, [class*="css"] {
        color: var(--text-primary);
        background: var(--bg-primary);
    }
    
    .stApp { 
        background: var(--bg-primary) !important; 
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        max-width: 900px !important;
    }

    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 2rem !important;
    }

    /* Sidebar Brand */
    .sidebar-brand {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        padding: 0 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .sidebar-brand-emoji {
        font-size: 1.5rem;
        filter: drop-shadow(0 0 8px var(--accent-glow));
    }

    /* New Chat Button */
    .new-chat-btn {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px var(--accent-glow) !important;
    }

    .new-chat-btn:hover {
        background: var(--accent-hover) !important;
        box-shadow: 0 4px 16px var(--accent-glow) !important;
        transform: translateY(-1px) !important;
    }

    /* Grade Level Radio Buttons */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 6px !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        color: white !important;
        box-shadow: 0 2px 8px var(--accent-glow) !important;
    }

    /* Sidebar History Buttons */
    section[data-testid="stSidebar"] .history-btn {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        justify-content: flex-start !important;
        padding: 10px 12px !important;
        border-radius: var(--radius-md) !important;
        margin: 3px 0 !important;
        width: 100% !important;
        text-align: left !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: all 0.15s ease !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] .history-btn:hover {
        background: var(--surface) !important;
        border-color: var(--border-subtle) !important;
        color: var(--text-primary) !important;
    }

    section[data-testid="stSidebar"] .history-btn-active {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    .section-divider {
        margin: 20px 0;
        border-top: 1px solid var(--border-subtle);
    }

    .section-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 10px;
        padding: 0 4px;
    }

    .time-group-label {
        font-size: 0.65rem;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 12px 0 6px 4px;
    }

    /* ========== MAIN CONTENT ========== */

    /* Empty State */
    .empty-state {
        text-align: center;
        margin-top: 12vh;
        animation: fadeInUp 0.6s ease;
    }

    .empty-glyph {
        font-size: 5rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 0 30px var(--accent-glow));
        animation: float 3s ease-in-out infinite;
    }

    .empty-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }

    .empty-sub {
        color: var(--text-secondary);
        font-size: 1rem;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        padding: 1.5rem 0 !important;
    }

    .stChatMessage[data-testid*="user"] {
        background: transparent !important;
    }

    .stChatMessage[data-testid*="assistant"] {
        background: transparent !important;
    }

    /* User Message Styling */
    .stChatMessage[data-testid*="user"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 16px 20px !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* Assistant Message Styling */
    .assistant-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--accent);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Tabs */
    .stTabs {
        margin-top: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        background: transparent !important;
        padding-bottom: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px !important;
        color: var(--text-muted) !important;
        background: transparent !important;
        border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
        background: var(--bg-tertiary) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        background: var(--bg-tertiary) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* Flashcards */
    .flashcard {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 18px;
        margin-bottom: 12px;
        font-size: 0.9rem;
        line-height: 1.7;
        color: var(--text-primary);
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }

    .flashcard:hover {
        border-color: var(--accent);
        box-shadow: 0 4px 12px var(--accent-glow);
        transform: translateY(-2px);
    }

    /* Info boxes */
    .stAlert {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-left: 3px solid var(--accent) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }

    /* Captions */
    .stCaptionContainer {
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
    }

    /* Chat Input */
    .stChatInputContainer {
        border-top: 1px solid var(--border-subtle) !important;
        background: var(--bg-primary) !important;
        padding: 1.5rem 0 !important;
    }

    .stChatInputContainer textarea {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        padding: 14px 18px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }

    .stChatInputContainer textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* Markdown Improvements */
    .stMarkdown h4 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    .stMarkdown p {
        line-height: 1.7;
        color: var(--text-secondary);
    }

    .stMarkdown ul {
        line-height: 1.8;
        color: var(--text-secondary);
    }

    .stMarkdown hr {
        border-color: var(--border-subtle) !important;
        margin: 1.5rem 0 !important;
    }

    /* Images */
    .stImage {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
    }

    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-15px);
        }
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* Loading State */
    .loading-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-muted);
        font-size: 0.9rem;
    }

    /* Timestamp Badge */
    .timestamp-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 4px 10px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
    }

    </style>
    """, unsafe_allow_html=True)

inject_css()

def _time_group(ts):
    """Group timestamps into Today, Yesterday, Earlier"""
    d = datetime.fromtimestamp(ts).date()
    today = date.today()
    if d == today: return "Today"
    if d == today - timedelta(days=1): return "Yesterday"
    return "Earlier"

# ─────────────────────────── SIDEBAR ───────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="sidebar-brand-emoji">🎓</span> EduGen AI</div>', unsafe_allow_html=True)
    
    # New Chat Button with custom styling
    col1, col2 = st.columns([1, 5])
    with col2:
        if st.button("✨  New Chat", use_container_width=True, key="new_chat", type="primary"):
            st.session_state.current_session_id = None
            st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Grade Level Section
    st.markdown('<div class="section-label">Learning Level</div>', unsafe_allow_html=True)
    valid_grades = ["Professional", "College", "School"]
    st.radio(
        "Grade Level",
        valid_grades,
        key="grade_level",
        label_visibility="collapsed",
        horizontal=False
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # History Section
    st.markdown('<div class="section-label">Chat History</div>', unsafe_allow_html=True)

    sessions = sorted(st.session_state.sessions.values(), key=lambda x: x["timestamp"], reverse=True)
    
    if not sessions:
        st.markdown('<div style="font-size:0.85rem; color:var(--text-muted); padding:12px 8px; text-align: center;">No conversations yet</div>', unsafe_allow_html=True)
    else:
        history_container = st.container(height=400, border=False)
        with history_container:
            grouped = {}
            for s in sessions:
                grouped.setdefault(_time_group(s["timestamp"]), []).append(s)

            for grp in ["Today", "Yesterday", "Earlier"]:
                if grp in grouped:
                    st.markdown(f'<div class="time-group-label">{grp}</div>', unsafe_allow_html=True)
                    for s in grouped[grp]:
                        is_active = (s["id"] == st.session_state.current_session_id)
                        title = s["title"][:32] + ("…" if len(s["title"]) > 32 else "")
                        
                        btn_class = "history-btn-active" if is_active else "history-btn"
                        
                        if st.button(
                            f"💬  {title}", 
                            key=f"hist_{s['id']}", 
                            use_container_width=True,
                            type="secondary" if not is_active else "primary"
                        ):
                            st.session_state.current_session_id = s['id']
                            st.rerun()


# ─────────────────────────── MAIN LAYOUT ───────────────────────────
current_id = st.session_state.current_session_id
active_session = st.session_state.sessions.get(current_id) if current_id else None

if not active_session:
    # Empty State
    st.markdown("""
        <div class="empty-state">
            <div class="empty-glyph">🎓</div>
            <div class="empty-title">What would you like to learn today?</div>
            <div class="empty-sub">
                Enter any concept or topic below. EduGen will create a personalized learning experience 
                with explanations, flashcards, and visual diagrams tailored to your level.
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    # Display conversation history
    for turn in active_session["turns"]:
        topic = turn["topic"]
        content = turn.get("content", {})
        images = turn.get("images", {})
        ts = turn.get("timestamp", time.time())
        ts_str = datetime.fromtimestamp(ts).strftime("%I:%M %p").lstrip("0")
        grade = turn.get("grade", "Any")
        
        # User Message
        with st.chat_message("user"):
            st.write(topic)
            st.markdown(f'<div class="timestamp-badge">📚 {grade} · 🕐 {ts_str}</div>', unsafe_allow_html=True)
        
        # Assistant Message
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown('<div class="assistant-header">🎓 EduGen AI</div>', unsafe_allow_html=True)
            
            tabs = st.tabs(["📖 Overview", "🗂️ Flashcards", "📊 Diagram"])
            
            # Overview Tab
            with tabs[0]:
                overview = content.get("overview", "")
                if overview:
                    st.markdown(overview)
                
                key_points = content.get("key_points", [])
                if key_points:
                    st.markdown("#### 🎯 Key Takeaways")
                    for p in key_points:
                        st.markdown(f"- {p}")
                
                real_world = content.get("real_world_example")
                if real_world:
                    st.markdown("#### 🌍 Real-World Context")
                    st.info(real_world)
                
                summary = content.get("summary")
                if summary:
                    st.markdown("---")
                    st.markdown("#### 📝 Summary")
                    st.write(summary)
            
            # Flashcards Tab
            with tabs[1]:
                fcs = content.get("flashcards", [])
                if not fcs:
                    st.markdown('<div style="text-align: center; padding: 2rem; color: var(--text-muted);">No flashcards available for this topic.</div>', unsafe_allow_html=True)
                else:
                    cols = st.columns(2)
                    for i, fc in enumerate(fcs):
                        with cols[i % 2]:
                            st.markdown(f'<div class="flashcard">{fc}</div>', unsafe_allow_html=True)
            
            # Diagram Tab
            with tabs[2]:
                diagram_b64 = images.get("diagram_b64")
                if diagram_b64:
                    try:
                        st.image(base64.b64decode(diagram_b64), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying diagram: {e}")
                else:
                    st.markdown('<div style="text-align: center; padding: 2rem; color: var(--text-muted);">No diagram available for this topic.</div>', unsafe_allow_html=True)

# ─────────────────────────── CHAT INPUT ───────────────────────────
if prompt := st.chat_input("Ask about any concept, topic, or idea..."):
    grade_level = st.session_state.grade_level
    payload = {
        "topic": prompt,
        "grade_level": grade_level,
    }

    # Show user message immediately
    with st.chat_message("user"):
        st.write(prompt)
        st.markdown(f'<div class="timestamp-badge">📚 {grade_level}</div>', unsafe_allow_html=True)
    
    # Show assistant response with loading
    with st.chat_message("assistant", avatar="🎓"):
        st.markdown('<div class="assistant-header">🎓 EduGen AI</div>', unsafe_allow_html=True)
        
        with st.spinner("✨ Generating your personalized learning content..."):
            try:
                # Content Generation
                content_res = requests.post(
                    f"{API_URL}/generate-content", 
                    json=payload,
                    timeout=300
                )
                
                if content_res.status_code != 200:
                    st.error(f"❌ API Error: {content_res.text}")
                    st.stop()
                
                content = content_res.json()

                if content.get("error"):
                    st.error(f"❌ {content['error']}")
                    st.stop()

                # Image Generation
                image_res = requests.post(
                    f"{API_URL}/generate-image", 
                    json=payload,
                    timeout=300
                )
                images = image_res.json() if image_res.status_code == 200 else {}
                
                # Create turn data
                turn_data = {
                    "topic": prompt,
                    "grade": grade_level,
                    "content": content,
                    "images": images,
                    "timestamp": time.time(),
                }

                # Update session state
                if not current_id:
                    new_id = str(uuid.uuid4())
                    st.session_state.sessions[new_id] = {
                        "id": new_id,
                        "title": prompt[:50],  # Limit title length
                        "timestamp": time.time(),
                        "turns": [turn_data]
                    }
                    st.session_state.current_session_id = new_id
                else:
                    st.session_state.sessions[current_id]["turns"].append(turn_data)
                    st.session_state.sessions[current_id]["timestamp"] = time.time()

                st.rerun()

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the API server. Please ensure it's running at " + API_URL)
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")