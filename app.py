import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. KINDGERECHTES DESIGN (BUTTONS & KUH OBEN) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #FFF9C4 0%, #FFECB3 100%);
    }
    
    /* Animation für die Kuh */
    @keyframes wiggle {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(8deg); }
        75% { transform: rotate(-8deg); }
        100% { transform: rotate(0deg); }
    }
    
    /* Kuh-Styling für die Leiste */
    .nav-cow {
        font-size: 60px;
        text-align: center;
        animation: wiggle 2s infinite ease-in-out;
        margin-top: -10px;
    }

    /* Startseite Buttons */
    .btn-lernen div button { background-color: #64B5F6 !important; border-radius: 50% !important; height: 160px; width: 160px; font-size: 80px !important; border: 8px solid white !important; }
    .btn-entdecken div button { background-color: #81C784 !important; border-radius: 50% !important; height: 160px; width: 160px; font-size: 80px !important; border: 8px solid white !important; }

    /* Zurück-Button (Links) */
    .back-btn div button {
        height: 75px !important;
        width: 75px !important;
        font-size: 35px !important;
        background-color: #FF8A65 !important;
        border-radius: 20px !important;
        border: 4px solid white !important;
    }

    /* Hör-Button (Rechts) */
    .play-btn div button {
        height: 75px !important;
        width: 75px !important;
        font-size: 40px !important;
        background-color: #FFD54F !important;
        border-radius: 20px !important;
        border: 4px solid white !important;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.08); }
        100% { transform: scale(1); }
    }

    /* Kamera-Eingabe kompakter rücken */
    .stCameraInput { margin-top: -20px; }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="font-size: 100px; text-align: center; margin-top: 20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 30px; font-family: Comic Sans MS;'>Kids Vision</p>", unsafe_allow_html=True)
    
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

# --- 4. SEITE 2: KAMERA-MODUS (KOMPAKTES DASHBOARD) ---
elif st.session_state['seite'] == 'kamera':
    # Die "Piloten-Leiste" ganz oben
    col_back, col_cow, col_play = st.columns([1, 1, 1])
    
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_cow:
        # Die Kuh begleitet das Kind oben in der Mitte
        st.markdown('<div class="nav-cow">🐮</div>', unsafe_allow_html=True)
        
    with col_play:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                st.snow()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Platzhalter, wenn noch kein Audio da ist (für symmetrisches Layout)
            st.markdown('<div style="height: 75px;"></div>', unsafe_allow_html=True)

    # Das Modus-Icon klein über der Kamera
    icon = "📖" if st.session_state['modus'] == "lernen" else "🔍"
    st.markdown(f"<p style='text-align: center; font-size: 30px; margin-bottom: 5px;'>{icon}</p>", unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            with st.spinner("✨"):
                prompt = "Du bist eine extrem liebe Kuh. Erkläre kurz (2 Sätze) für ein Kind, was du auf dem Foto siehst. Sei sehr herzlich!"
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
                st.rerun()
