import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision", page_icon="👀", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. DESIGN (KOMPAKT & ZENTRIERT) ---
st.markdown("""
    <style>
    /* Hintergrund & Grundgerüst fixieren gegen Scrollen */
    .stApp {
        background: linear-gradient(180deg, #e3f2fd 0%, #f1f8e9 100%);
        overflow: hidden;
    }
    
    .kids-title {
        font-size: 38px;
        color: #2e7d32;
        text-align: center;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        margin-bottom: 5px;
    }

    /* Modus-Buttons schmaler */
    div.stButton > button {
        border-radius: 25px;
        height: 80px;
        font-size: 40px !important;
        border: none;
    }
    
    .btn-lernen div button { background-color: #42a5f5 !important; border-bottom: 5px solid #1e88e5 !important; }
    .btn-entdecken div button { background-color: #66bb6a !important; border-bottom: 5px solid #43a047 !important; }

    /* ZENTRIERTER PLAY-BUTTON */
    .play-container {
        display: flex;
        justify-content: center;
        margin-top: 10px;
    }
    
    .play-btn div button {
        background-color: #ffca28 !important;
        border-bottom: 6px solid #ffb300 !important;
        height: 100px !important;
        width: 150px !important;
        font-size: 50px !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Kamera-Größe begrenzen */
    .stCameraInput {
        margin-top: -10px;
    }
    
    .back-btn div button {
        height: 40px;
        font-size: 16px !important;
        background-color: #ef5350 !important;
        color: white !important;
        width: 80px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation
if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="kids-title">👀 Kids Vision</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 10px;'>Wähle aus:</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-MODUS (ONE-PAGE) ---
elif st.session_state['seite'] == 'kamera':
    # Kompakter Header
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    icon = "📖" if st.session_state['modus'] == "lernen" else "🔍"
    st.markdown(f"<h2 style='text-align: center; margin-top: -45px;'>{icon}</h2>", unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            with st.spinner("🧙‍♂️..."):
                prompt = "Erkläre kurz in 2 Sätzen für ein Kind."
                base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                audio_res = client.audio.speech.create(model="tts-1", voice="shimmer", input=res.choices[0].message.content)
                st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')

        # HÖR-BUTTON IN DER MITTE
        if 'audio' in st.session_state:
            st.markdown('<div class="play-container"><div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
