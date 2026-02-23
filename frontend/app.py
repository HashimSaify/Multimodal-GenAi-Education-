import base64
import streamlit as st
import requests
import time
import uuid
from datetime import datetime, date, timedelta

API_URL = "https://multimodal-genai-education.onrender.com"

st.set_page_config(
    page_title="EduGen AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
defaults = {
    "sessions": {},
    "current_session_id": None,
    "grade_level": "Professional",
    "_scroll_to_top": False,
    "_scroll_to_bottom": False,
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
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

    :root {
        --bg:             #06060a;
        --bg-2:           #0d0d14;
        --bg-3:           #12121c;
        --bg-4:           #17172380;
        --sidebar-bg:     #080810;
        --surface:        #1a1a27;
        --surface-2:      #20202f;
        --border:         rgba(120,120,200,0.12);
        --border-2:       rgba(120,120,200,0.22);
        --text:           #eeeef5;
        --text-2:         #9898b4;
        --text-3:         #55556e;
        --gold:           #c9a84c;
        --gold-2:         #e8c97a;
        --gold-glow:      rgba(201,168,76,0.18);
        --gold-glow-2:    rgba(201,168,76,0.06);
        --violet:         #7c6ff7;
        --violet-dim:     rgba(124,111,247,0.14);
        --radius:         12px;
        --radius-lg:      18px;
        --radius-xl:      26px;
    }

    *, *::before, *::after {
        font-family: 'DM Sans', system-ui, sans-serif;
        box-sizing: border-box;
    }

    h1, h2, h3, h4, .serif {
        font-family: 'DM Serif Display', Georgia, serif;
    }

    html, body, [class*="css"] {
        background: var(--bg) !important;
        color: var(--text);
    }

    .stApp {
        background: var(--bg) !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(124,111,247,0.06) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(201,168,76,0.04) 0%, transparent 60%) !important;
        background-attachment: fixed !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    section.main > div:first-child {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 7rem !important;
        padding-left: clamp(1.5rem, 4vw, 3rem) !important;
        padding-right: clamp(1.5rem, 4vw, 3rem) !important;
        max-width: 860px !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        overflow-anchor: none !important;
    }

    section.main {
        overflow-anchor: none !important;
    }

    section.main > div {
        overflow-anchor: none !important;
    }

    /* ============================================================
       SIDEBAR
    ============================================================ */
    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding: 2rem 1.2rem 1.5rem !important;
    }

    /* Brand */
    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 2rem;
    }

    .brand-mark {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #c9a84c 0%, #7c6ff7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 16px var(--gold-glow);
        flex-shrink: 0;
    }

    .brand-text {
        font-family: 'DM Serif Display', serif;
        font-size: 1.25rem;
        color: var(--text);
        letter-spacing: -0.01em;
    }

    .brand-text span {
        color: var(--gold);
    }

    /* New Chat button */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #c9a84c 0%, #b8942e 100%) !important;
        color: #06060a !important;
        border: none !important;
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 11px 18px !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 2px 12px var(--gold-glow) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 24px rgba(201,168,76,0.35) !important;
        transform: translateY(-1px) !important;
        filter: brightness(1.08) !important;
    }

    /* Grade radio */
    .grade-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-3);
        margin-bottom: 10px;
        padding-left: 2px;
    }

    section[data-testid="stSidebar"] .stRadio > div {
        gap: 5px !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label {
        background: var(--bg-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 9px 14px !important;
        margin: 0 !important;
        color: var(--text-2) !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        transition: all 0.18s !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--surface) !important;
        border-color: var(--border-2) !important;
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(201,168,76,0.18) 0%, rgba(124,111,247,0.12) 100%) !important;
        border-color: var(--gold) !important;
        color: var(--gold-2) !important;
        box-shadow: inset 0 0 0 1px rgba(201,168,76,0.15) !important;
    }

    /* Divider */
    .sidebar-divider {
        height: 1px;
        background: var(--border);
        margin: 18px 0;
    }

    /* ============================================================
       CHAT HISTORY — IMPROVED
    ============================================================ */

    /* Section label with extending hairline rule */
    .hist-group-label {
        font-size: 0.60rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-3);
        margin: 14px 0 3px 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .hist-group-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--border-2), transparent);
    }

    /* Scroll container */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        background: transparent !important;
    }

    /* ── Inactive history button ── */
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        color: var(--text-3) !important;
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        padding: 6px 10px 6px 11px !important;
        border-radius: 0 8px 8px 0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition:
            background 0.16s ease,
            color 0.16s ease,
            border-color 0.16s ease,
            padding-left 0.16s ease !important;
        width: 100% !important;
        letter-spacing: 0 !important;
        line-height: 1.5 !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.035) !important;
        border-left-color: rgba(201, 168, 76, 0.4) !important;
        color: var(--text-2) !important;
        padding-left: 15px !important;
        box-shadow: none !important;
        transform: none !important;
        filter: none !important;
    }

    /* ── Active / selected history button ──
       Override the gold "New Chat" primary style only for history items.
       We use the :not([key="new_chat"]) trick via data attributes.
       Streamlit doesn't expose key on the DOM, so we target by order:
       the New Chat button is always the FIRST primary button in sidebar.
       History active items come after → we override with higher specificity.
    */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button[kind="primary"] {
        background: linear-gradient(
            90deg,
            rgba(201, 168, 76, 0.14) 0%,
            rgba(201, 168, 76, 0.03) 100%
        ) !important;
        color: var(--gold-2) !important;
        border: none !important;
        border-left: 2px solid var(--gold) !important;
        border-radius: 0 8px 8px 0 !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 6px 10px 6px 13px !important;
        letter-spacing: 0 !important;
        line-height: 1.5 !important;
        box-shadow: none !important;
        transition: background 0.16s ease !important;
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transform: none !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton > button[kind="primary"]:hover,
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(
            90deg,
            rgba(201, 168, 76, 0.20) 0%,
            rgba(201, 168, 76, 0.06) 100%
        ) !important;
        box-shadow: none !important;
        filter: none !important;
        transform: none !important;
    }

    /* No history placeholder */
    .no-history {
        text-align: center;
        padding: 22px 8px 14px;
        color: var(--text-3);
        font-size: 0.80rem;
        line-height: 1.75;
    }

    .no-history-icon {
        font-size: 1.4rem;
        margin-bottom: 8px;
        opacity: 0.3;
        display: block;
    }

    /* ============================================================
       EMPTY STATE
    ============================================================ */
    .hero-icon-img {
        width: clamp(72px, 12vw, 96px);
        height: clamp(72px, 12vw, 96px);
        border-radius: 22px;
        background: linear-gradient(145deg, #d4b483 0%, #a89070 40%, #7c6ff7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        margin: 0 auto 1.6rem;
        box-shadow:
            0 0 0 10px rgba(201,168,76,0.06),
            0 8px 40px rgba(201,168,76,0.2),
            0 0 80px rgba(124,111,247,0.12);
        animation: pulse-ring 3s ease-in-out infinite;
        flex-shrink: 0;
    }

    .hero-eyebrow {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: var(--gold);
        margin-bottom: 1rem;
        text-align: center;
    }

    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: clamp(2rem, 4.5vw, 2.8rem);
        color: var(--text);
        margin-bottom: 1.1rem;
        letter-spacing: -0.03em;
        line-height: 1.15;
        text-align: center;
    }

    .hero-title em {
        font-style: italic;
        color: var(--gold-2);
    }

    .hero-sub {
        color: var(--text-2);
        font-size: clamp(0.88rem, 2vw, 1rem);
        max-width: 440px;
        margin: 0 auto 2.2rem;
        line-height: 1.75;
        font-weight: 300;
        text-align: center;
    }

    .suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        width: 100%;
        max-width: 560px;
        margin: 0 auto;
    }

    .suggestion-pill {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 100px;
        padding: 8px 16px;
        font-size: 0.83rem;
        color: var(--text-2);
        font-weight: 500;
        white-space: nowrap;
        transition: all 0.18s;
        cursor: default;
    }

    .suggestion-pill:hover {
        background: var(--surface-2);
        border-color: var(--gold);
        color: var(--gold-2);
    }

    /* ============================================================
       CHAT MESSAGES
    ============================================================ */
    .stChatMessage {
        background: transparent !important;
        padding: 1.25rem 0 !important;
    }

    .stChatMessage[data-testid*="user"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: var(--radius-lg) !important;
        padding: 15px 20px !important;
    }

    .stChatMessage[data-testid*="assistant"] .stChatMessageAvatarAssistant {
        background: linear-gradient(135deg, #c9a84c, #7c6ff7) !important;
        border-radius: 10px !important;
    }

    .response-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }

    .response-header-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--gold), var(--violet));
        box-shadow: 0 0 8px var(--gold-glow);
        flex-shrink: 0;
    }

    .response-header-text {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--gold);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .meta-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: var(--bg-4);
        border: 1px solid var(--border);
        border-radius: 100px;
        font-size: 0.74rem;
        color: var(--text-3);
        margin-top: 8px;
        font-weight: 500;
    }

    /* ============================================================
       TABS
    ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        border-bottom: 1px solid var(--border) !important;
        background: transparent !important;
        padding: 0 !important;
        margin-bottom: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px !important;
        color: var(--text-3) !important;
        background: transparent !important;
        border-radius: 10px 10px 0 0 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        border: none !important;
        letter-spacing: 0.01em !important;
        transition: all 0.18s !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-2) !important;
        background: var(--bg-3) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--gold-2) !important;
        background: var(--bg-3) !important;
        border-bottom: 2px solid var(--gold) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.6rem !important;
        background: transparent !important;
    }

    /* ============================================================
       CONTENT BLOCKS
    ============================================================ */
    .stMarkdown h4 {
        font-family: 'DM Serif Display', serif;
        color: var(--text);
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 1.8rem;
        margin-bottom: 0.8rem;
        letter-spacing: -0.01em;
    }

    .stMarkdown p {
        line-height: 1.75;
        color: var(--text-2);
        font-size: 0.95rem;
        font-weight: 300;
    }

    .stMarkdown ul {
        line-height: 1.85;
        color: var(--text-2);
    }

    .stMarkdown ul li::marker {
        color: var(--gold);
    }

    .stMarkdown hr {
        border-color: var(--border) !important;
        margin: 1.8rem 0 !important;
    }

    .fc-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(min(260px, 100%), 1fr));
        gap: 14px;
        width: 100%;
    }

    .flashcard {
        position: relative;
        background: var(--bg-3);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px;
        margin-bottom: 14px;
        font-size: 0.88rem;
        line-height: 1.75;
        color: var(--text-2);
        transition: all 0.22s cubic-bezier(.16,1,.3,1);
        overflow: hidden;
    }

    .flashcard::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, var(--gold), var(--violet));
        opacity: 0;
        transition: opacity 0.22s;
    }

    .flashcard:hover {
        border-color: rgba(201,168,76,0.3);
        background: var(--surface);
        color: var(--text);
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(201,168,76,0.08);
    }

    .flashcard:hover::before {
        opacity: 1;
    }

    .flashcard-num {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-3);
        margin-bottom: 8px;
    }

    .stAlert {
        background: linear-gradient(135deg, rgba(201,168,76,0.07) 0%, rgba(124,111,247,0.05) 100%) !important;
        border: 1px solid rgba(201,168,76,0.18) !important;
        border-left: 3px solid var(--gold) !important;
        border-radius: var(--radius) !important;
        color: var(--text-2) !important;
        font-size: 0.9rem !important;
    }

    .stImage {
        border-radius: var(--radius-lg);
        overflow: hidden;
        border: 1px solid var(--border);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    /* ============================================================
       CHAT INPUT
    ============================================================ */
    .stChatInputContainer {
        background: transparent !important;
        border-top: 1px solid var(--border) !important;
        padding: 1.2rem clamp(0.75rem, 4vw, 3rem) !important;
        backdrop-filter: blur(20px) !important;
    }

    .stChatInputContainer > div {
        max-width: min(860px, 100%) !important;
        margin-left: auto !important;
        margin-right: auto !important;
        background: var(--surface) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: var(--radius-xl) !important;
        box-shadow: 0 0 0 4px rgba(201,168,76,0.03), 0 4px 24px rgba(0,0,0,0.3) !important;
        overflow: hidden !important;
        transition: all 0.22s !important;
    }

    .stChatInputContainer > div:focus-within {
        border-color: rgba(201,168,76,0.4) !important;
        box-shadow: 0 0 0 4px var(--gold-glow-2), 0 4px 32px rgba(0,0,0,0.3) !important;
    }

    .stChatInputContainer textarea {
        background: transparent !important;
        border: none !important;
        color: var(--text) !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        padding: 16px 20px !important;
        line-height: 1.5 !important;
    }

    .stChatInputContainer textarea::placeholder {
        color: var(--text-3) !important;
    }

    .stChatInputContainer button {
        background: linear-gradient(135deg, var(--gold) 0%, #b8942e 100%) !important;
        border-radius: 12px !important;
        margin: 8px !important;
        color: #06060a !important;
        border: none !important;
        transition: all 0.18s !important;
    }

    .stChatInputContainer button:hover {
        filter: brightness(1.1) !important;
        box-shadow: 0 4px 16px var(--gold-glow) !important;
    }

    /* ============================================================
       SPINNER
    ============================================================ */
    .stSpinner > div {
        border-top-color: var(--gold) !important;
    }

    /* ============================================================
       SCROLLBAR
    ============================================================ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

    /* ============================================================
       ANIMATIONS
    ============================================================ */
    @keyframes riseIn {
        from { opacity: 0; transform: translateY(28px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    @keyframes pulse-ring {
        0%, 100% {
            box-shadow: 0 0 0 10px rgba(201,168,76,0.06),
                        0 8px 40px rgba(201,168,76,0.2),
                        0 0 80px rgba(124,111,247,0.12);
        }
        50% {
            box-shadow: 0 0 0 18px rgba(201,168,76,0.03),
                        0 8px 60px rgba(201,168,76,0.3),
                        0 0 100px rgba(124,111,247,0.18);
        }
    }

    .stCaptionContainer, .caption { color: var(--text-3) !important; font-size: 0.78rem !important; }

    /* ============================================================
       RESPONSIVE — TABLET  (≤ 900px)
    ============================================================ */
    @media (max-width: 900px) {
        .block-container {
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
        }

        .hero-title {
            font-size: clamp(1.6rem, 5vw, 2.2rem) !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 14px !important;
            font-size: 0.8rem !important;
        }
    }

    /* ============================================================
       RESPONSIVE — MOBILE  (≤ 640px)
    ============================================================ */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-bottom: 8rem !important;
        }

        .hero-title {
            font-size: 1.5rem !important;
            letter-spacing: -0.02em !important;
        }

        .hero-sub {
            font-size: 0.88rem !important;
        }

        .hero-icon-img {
            width: 68px !important;
            height: 68px !important;
            font-size: 1.8rem !important;
            border-radius: 18px !important;
        }

        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        .flashcard {
            margin-bottom: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 7px 10px !important;
            font-size: 0.75rem !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 2px !important;
        }

        .suggestions {
            gap: 6px !important;
        }

        .suggestion-pill {
            font-size: 0.75rem !important;
            padding: 6px 11px !important;
        }

        .brand-text {
            font-size: 1.05rem !important;
        }

        .stChatInputContainer > div {
            border-radius: 14px !important;
        }

        .stChatMessage {
            padding: 0.75rem 0 !important;
        }

        .response-header {
            margin-bottom: 0.8rem !important;
            padding-bottom: 0.7rem !important;
        }
    }

    /* ============================================================
       RESPONSIVE — VERY SMALL  (≤ 400px)
    ============================================================ */
    @media (max-width: 400px) {
        .hero-title {
            font-size: 1.3rem !important;
        }

        .hero-eyebrow {
            font-size: 0.62rem !important;
            letter-spacing: 0.12em !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 6px 8px !important;
            font-size: 0.7rem !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)

inject_css()

# Inject JS to prevent Streamlit from auto-scrolling to bottom on reruns
st.markdown("""
<script>
(function() {
    const win = window.parent;
    const s = win.document.createElement('style');
    s.id = 'no-scroll-anchor';
    if (!win.document.getElementById('no-scroll-anchor')) {
        s.textContent = '.main, .main *, section.main > div { overflow-anchor: none !important; }';
        win.document.head.appendChild(s);
    }
    const main = win.document.querySelector('section.main');
    if (main && main.scrollTop < 50) {
        main.scrollTo({ top: 0, behavior: 'instant' });
    }
})();
</script>
""", unsafe_allow_html=True)

def _time_group(ts):
    d = datetime.fromtimestamp(ts).date()
    today = date.today()
    if d == today: return "Today"
    if d == today - timedelta(days=1): return "Yesterday"
    return "Earlier"

# ─────────────────────────── SIDEBAR ───────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="brand">
            <div class="brand-mark">🎓</div>
            <div class="brand-text">Edu<span>Gen</span> AI</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✦  New Conversation", use_container_width=True, key="new_chat", type="primary"):
        st.session_state.current_session_id = None
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="grade-label">Learning Level</div>', unsafe_allow_html=True)
    valid_grades = ["Professional", "College", "School"]
    st.radio(
        "Grade Level",
        valid_grades,
        key="grade_level",
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="grade-label">Chat History</div>', unsafe_allow_html=True)

    sessions = sorted(st.session_state.sessions.values(), key=lambda x: x["timestamp"], reverse=True)

    if not sessions:
        st.markdown("""
            <div class="no-history">
                <span class="no-history-icon">📭</span>
                No conversations yet.<br>Ask your first question below.
            </div>
        """, unsafe_allow_html=True)
    else:
        history_container = st.container(height=420, border=False)
        with history_container:
            grouped = {}
            for s in sessions:
                grouped.setdefault(_time_group(s["timestamp"]), []).append(s)

            for grp in ["Today", "Yesterday", "Earlier"]:
                if grp in grouped:
                    st.markdown(f'<div class="hist-group-label">{grp}</div>', unsafe_allow_html=True)
                    for s in grouped[grp]:
                        is_active = (s["id"] == st.session_state.current_session_id)
                        title = s["title"][:34] + ("…" if len(s["title"]) > 34 else "")
                        if st.button(
                            title,
                            key=f"hist_{s['id']}",
                            use_container_width=True,
                            type="primary" if is_active else "secondary"
                        ):
                            st.session_state.current_session_id = s["id"]
                            st.rerun()

# ─────────────────────────── MAIN LAYOUT ───────────────────────────
current_id = st.session_state.current_session_id
active_session = st.session_state.sessions.get(current_id) if current_id else None

if st.session_state.get("_scroll_to_top"):
    st.markdown("""
    <script>
    (function() {
        const main = window.parent.document.querySelector('section.main');
        if (main) main.scrollTo({ top: 0, behavior: 'instant' });
    })();
    </script>
    """, unsafe_allow_html=True)
    st.session_state._scroll_to_top = False

if not active_session:
    st.markdown("""
        <div style="width:100%;min-height:72vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:clamp(2rem,8vh,5rem) clamp(1rem,5vw,2rem) 3rem;text-align:center;">
            <div class="hero-icon-img">🎓</div>
            <div class="hero-eyebrow">Your personal AI tutor</div>
            <h1 class="hero-title">What would you like to<br><em>learn today?</em></h1>
            <p class="hero-sub">Enter any concept or topic below. EduGen creates a personalized learning experience with explanations, flashcards, and diagrams — tailored to your level.</p>
            <div class="suggestions">
                <div class="suggestion-pill">⚛️ Quantum entanglement</div>
                <div class="suggestion-pill">📈 Machine learning basics</div>
                <div class="suggestion-pill">🧬 CRISPR gene editing</div>
                <div class="suggestion-pill">🌍 Climate systems</div>
                <div class="suggestion-pill">💡 Neural networks</div>
                <div class="suggestion-pill">⚖️ Constitutional law</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

else:
    for turn in active_session["turns"]:
        topic   = turn["topic"]
        content = turn.get("content", {})
        images  = turn.get("images", {})
        ts      = turn.get("timestamp", time.time())
        ts_str  = datetime.fromtimestamp(ts).strftime("%I:%M %p").lstrip("0")
        grade   = turn.get("grade", "Any")

        with st.chat_message("user"):
            st.write(topic)
            st.markdown(
                f'<div class="meta-pill">📚 {grade} &nbsp;·&nbsp; 🕐 {ts_str}</div>',
                unsafe_allow_html=True
            )

        with st.chat_message("assistant", avatar="🎓"):
            st.markdown("""
                <div class="response-header">
                    <div class="response-header-dot"></div>
                    <div class="response-header-text">EduGen Response</div>
                </div>
            """, unsafe_allow_html=True)

            tabs = st.tabs(["📖  Overview", "🗂  Flashcards", "📊  Diagram"])

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

            with tabs[1]:
                fcs = content.get("flashcards", [])
                if not fcs:
                    st.markdown(
                        '<div style="text-align:center;padding:2.5rem;color:var(--text-3)">No flashcards available.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    cards_html = '<div class="fc-grid">'
                    for i, fc in enumerate(fcs):
                        cards_html += f'<div class="flashcard"><div class="flashcard-num">Card {i+1:02d}</div>{fc}</div>'
                    cards_html += '</div>'
                    st.markdown(cards_html, unsafe_allow_html=True)

            with tabs[2]:
                diagram_b64 = images.get("diagram_b64")
                if diagram_b64:
                    try:
                        st.image(base64.b64decode(diagram_b64), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying diagram: {e}")
                else:
                    st.markdown(
                        '<div style="text-align:center;padding:2.5rem;color:var(--text-3)">No diagram generated for this topic.</div>',
                        unsafe_allow_html=True
                    )

# Bottom anchor
st.markdown('<div id="edugen-bottom-anchor" style="height:1px;"></div>', unsafe_allow_html=True)

if st.session_state.get("_scroll_to_bottom"):
    st.markdown("""
    <script>
    (function() {
        function scrollToBottom() {
            const main = window.parent.document.querySelector('section.main');
            const anchor = window.parent.document.getElementById('edugen-bottom-anchor');
            if (anchor) {
                anchor.scrollIntoView({ behavior: 'smooth', block: 'end' });
            } else if (main) {
                main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' });
            }
        }
        setTimeout(scrollToBottom, 120);
    })();
    </script>
    """, unsafe_allow_html=True)
    st.session_state._scroll_to_bottom = False

# ─────────────────────────── CHAT INPUT ───────────────────────────
if prompt := st.chat_input("Ask about any concept, topic, or idea…"):
    grade_level = st.session_state.grade_level
    payload = {"topic": prompt, "grade_level": grade_level}

    with st.chat_message("user"):
        st.write(prompt)
        st.markdown(f'<div class="meta-pill">📚 {grade_level}</div>', unsafe_allow_html=True)

    st.markdown("""
    <script>
    (function() {
        function scrollNow() {
            const main = window.parent.document.querySelector('section.main');
            if (main) main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' });
        }
        setTimeout(scrollNow, 80);
    })();
    </script>
    """, unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🎓"):
        st.markdown("""
            <div class="response-header">
                <div class="response-header-dot"></div>
                <div class="response-header-text">EduGen Response</div>
            </div>
        """, unsafe_allow_html=True)

        with st.spinner("✦ Crafting your personalized lesson…"):
            try:
                content_res = requests.post(f"{API_URL}/generate-content", json=payload, timeout=300)
                if content_res.status_code != 200:
                    st.error(f"❌ API Error: {content_res.text}")
                    st.stop()
                content = content_res.json()
                if content.get("error"):
                    st.error(f"❌ {content['error']}")
                    st.stop()

                image_res = requests.post(f"{API_URL}/generate-image", json=payload, timeout=300)
                images = image_res.json() if image_res.status_code == 200 else {}

                turn_data = {
                    "topic": prompt, "grade": grade_level,
                    "content": content, "images": images,
                    "timestamp": time.time(),
                }

                if not current_id:
                    new_id = str(uuid.uuid4())
                    st.session_state.sessions[new_id] = {
                        "id": new_id, "title": prompt[:50],
                        "timestamp": time.time(), "turns": [turn_data]
                    }
                    st.session_state.current_session_id = new_id
                    st.session_state._scroll_to_top = True
                else:
                    st.session_state.sessions[current_id]["turns"].append(turn_data)
                    st.session_state.sessions[current_id]["timestamp"] = time.time()

                st.session_state._scroll_to_bottom = True
                st.rerun()

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 Cannot connect to API at {API_URL}. Please ensure it's running.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")