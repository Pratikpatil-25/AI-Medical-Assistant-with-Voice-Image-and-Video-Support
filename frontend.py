import os
import base64
import requests
import streamlit as st
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder

st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .main { background-color: #0e1117; }

        .hero {
            padding: 1.75rem 2rem;
            border-radius: 16px;
            background: linear-gradient(135deg, #0f766e 0%, #134e4a 100%);
            margin-bottom: 1.75rem;
        }
        .hero h1 {
            color: #ffffff;
            font-size: 1.9rem;
            margin-bottom: 0.25rem;
        }
        .hero p {
            color: #d1fae5;
            font-size: 0.95rem;
            margin: 0;
        }

        .step-card {
            background-color: #1a1f2b;
            border: 1px solid #2d3444;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
        }
        .step-title {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-weight: 600;
            font-size: 1.05rem;
            color: #f0f0f0;
            margin-bottom: 0.75rem;
        }
        .step-number {
            background-color: #0f766e;
            color: white;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            flex-shrink: 0;
        }
        .badge {
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-ready { background-color: #064e3b; color: #6ee7b7; }
        .badge-empty { background-color: #3f3f46; color: #a1a1aa; }

        .response-card {
            background-color: #14201d;
            border: 1px solid #1f5f4f;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-top: 1rem;
        }
        .response-label {
            color: #6ee7b7;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .transcript-box {
            background-color: #1a1f2b;
            border-left: 3px solid #0f766e;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            color: #d1d5db;
            font-style: italic;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar - configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    default_backend = os.environ.get("BACKEND_URL", "http://localhost:8000")
    backend_url = st.text_input("Backend URL", value=default_backend)
    st.markdown("---")
    st.markdown(
        """
        **How it works**
        1. Record your voice
        2. Optionally attach an image or video
        3. Send to the AI doctor
        4. Response plays automatically 🔊
        """
    )
    st.markdown("---")
    st.caption("⚠️ For informational purposes only. Not a substitute for professional medical advice.")

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🩺 AI Medical Assistant</h1>
        <p>Speak your symptoms, share visuals, and get an instant spoken diagnosis from your AI doctor.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Step 1: Record audio
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="step-card">
        <div class="step-title"><span class="step-number">1</span> Record your voice</div>
    """,
    unsafe_allow_html=True,
)
audio_bytes = audio_recorder(
    text="Click the mic to start / stop recording",
    icon_size="2x",
    pause_threshold=3.0,
)
if audio_bytes:
    st.markdown('<span class="badge badge-ready">✓ Audio recorded</span>', unsafe_allow_html=True)
    st.audio(audio_bytes, format="audio/wav")
else:
    st.markdown('<span class="badge badge-empty">No audio yet</span>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Step 2 & 3: Image and video, side by side
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-title"><span class="step-number">2</span> Attach an image</div>
        """,
        unsafe_allow_html=True,
    )
    image_file = st.file_uploader(
        "Optional", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )
    if image_file:
        st.image(image_file, use_container_width=True)
        st.markdown('<span class="badge badge-ready">✓ Image attached</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-empty">None attached</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-title"><span class="step-number">3</span> Attach a video</div>
        """,
        unsafe_allow_html=True,
    )
    video_file = st.file_uploader(
        "Optional", type=["mp4", "mov", "avi"], label_visibility="collapsed"
    )
    if video_file:
        st.video(video_file)
        st.markdown('<span class="badge badge-ready">✓ Video attached</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-empty">None attached</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Step 4: Submit
# ---------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
submit = st.button("🚀 Send to AI Doctor", type="primary", use_container_width=True)

if submit:
    if not audio_bytes:
        st.warning("Please record your voice before sending.")
    else:
        with st.spinner("The AI doctor is analyzing your query..."):
            files = {"audio": ("patient_query.wav", audio_bytes, "audio/wav")}
            if image_file is not None:
                files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
            if video_file is not None:
                files["video"] = (video_file.name, video_file.getvalue(), video_file.type)

            try:
                response = requests.post(f"{backend_url}/ask", files=files, timeout=180)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                st.error(f"Request to backend failed: {e}")
                data = None
            else:
                data = response.json()

        if data:
            st.markdown(
                """
                <div class="response-card">
                    <div class="response-label">Transcribed query</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="transcript-box">"{data["transcription"]}"</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div class="response-card">
                    <div class="response-label">🩺 Doctor's response</div>
                """,
                unsafe_allow_html=True,
            )
            st.write(data["doctor_response"])
            st.markdown("</div>", unsafe_allow_html=True)

            # --- Autoplay audio the instant it's rendered ---
            audio_b64 = data["audio_base64"]
            components.html(
                f"""
                <audio autoplay controls style="width: 100%; margin-top: 12px;">
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                </audio>
                """,
                height=60,
            )