import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision", page_icon="🐻", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. KINDGERECHTES DESIGN (OPTIMIERT) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #FFF9C4 0%, #FFECB3 100%);
        overflow: hidden;
    }
    
    /* Animationen */
    @keyframes wiggle {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(5deg); }
        75% { transform: rotate(-5deg); }
        100% { transform: rotate(0deg); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    /* Der FRÖHLICHE Bär */
    .magic-bear {
        font-size: 90px;
        text-align: center;
        margin-top: 0px;
        margin-bottom: -10px;
        animation: wiggle 2s infinite ease-in-out;
    }

    /* Startseite Kreise */
    div.stButton > button {
        border-radius: 50% !important;
        width: 140px !important;
        height: 140px !important;
        font-size: 70px !important;
        border: 6px solid white !important;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    div.stButton > button:hover { transform: scale(1.05); }
    
    .btn-lernen div button { background-color: #64B5F6 !important; }
    .btn-entdecken div button { background-color: #81C784 !important; }

    /* KOMPAKTE KAMERA-ANSICHT */
    .back-btn div button {
        height: 50px !important;
        width: 50px !important;
        font-size: 25px !important;
        background-color: #FF8A65 !important;
        border-radius: 50% !important;
    }
    
    .stCameraInput {
        border-radius: 20px;
        margin-top: -10px;
        margin-bottom: 5px;
    }

    /* ZENTRIERTER, ATMENDER PLAY-BUTTON */
    .play-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: -15px; /* Richtig weit nach oben! */
    }
    
    .play-btn div button {
        background-color: #FFD54F !important;
        border-radius: 50% !important;
        width: 120px !important;
        height: 120px !important;
        font-size: 70px !important;
        border: 6px solid #FFB300 !important;
        animation: pulse 1.5s infinite; /* Langsames Atmen */
    }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    # Ein Bären-Emoji, das auf den meisten Systemen freundlich lächelt
    st.markdown('<div class="magic-bear">🐻‍❄️</div>', unsafe_allow_html=True)
    
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

# --- 4. SEITE 2: KAMERA-MODUS ---
elif st.session_state['seite'] == 'kamera':
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"): # Nur der Pfeil!
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    icon = "📖" if st.session_state['modus'] == "lernen" else "🔍"
    st.markdown(f"<h1 style='text-align: center; margin-top: -55px;'>{icon}</h1>", unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            with st.spinner("🐻..."):
                prompt = "Du bist ein extrem lieber, freundlicher Kuschelbär. Erkläre kurz (2 Sätze) für ein Kind (5 Jahre), was du siehst. Sei sehr motivierend!"
                base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                audio_res = client.audio.speech.create(model="tts-1", voice="alloy", input=res.choices[0].message.content)
                st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')

        if 'audio' in st.session_state:
            # Der Bär erscheint fröhlich über dem Button, wenn er fertig ist
            st.markdown('<div class="magic-bear" style="font-size:60px;">🐻‍❄️</div>', unsafe_allow_html=True)
            st.markdown('<div class="play-container"><div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                st.snow() # Dezenter Konfetti-Ersatz
            st.markdown('</div></div>', unsafe_allow_html=True)
