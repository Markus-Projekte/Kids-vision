import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision", page_icon="✨", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. KINDERGARTEN-DESIGN (KEIN TEXT, NUR MAGIE) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #FFF9C4 0%, #FFECB3 100%);
        overflow: hidden;
    }
    
    .magic-title {
        font-size: 80px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    /* Startseite Buttons: Riesig und rund */
    .mode-container {
        display: flex;
        justify-content: space-around;
        padding-top: 20px;
    }

    div.stButton > button {
        border-radius: 50% !important; /* Kreisrund */
        width: 160px !important;
        height: 160px !important;
        font-size: 80px !important;
        transition: transform 0.3s;
        border: 8px solid white !important;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.1);
    }
    
    .btn-lernen div button { background-color: #64B5F6 !important; }
    .btn-entdecken div button { background-color: #81C784 !important; }

    /* Der goldene Play-Button in der Mitte */
    .play-container {
        display: flex;
        justify-content: center;
        margin-top: 5px;
    }
    
    .play-btn div button {
        background-color: #FFD54F !important;
        border-radius: 40px !important;
        width: 200px !important;
        height: 120px !important;
        font-size: 70px !important;
        border: 6px solid white !important;
    }

    /* Zurück-Pfeil oben links */
    .back-btn div button {
        height: 60px !important;
        width: 60px !important;
        font-size: 30px !important;
        background-color: #FF8A65 !important;
        border-radius: 50% !important;
    }
    
    /* Kamera-Vorschau abrunden */
    .stCameraInput {
        border-radius: 30px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation
if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. STARTSEITE (REIN VISUELL) ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="magic-title">✨</div>', unsafe_allow_html=True)
    
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

# --- 4. KAMERA-MODUS (KOMPAKT) ---
elif st.session_state['seite'] == 'kamera':
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    icon = "📖" if st.session_state['modus'] == "lernen" else "🔍"
    st.markdown(f"<h1 style='text-align: center; margin-top: -60px;'>{icon}</h1>", unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            with st.spinner("✨..."):
                # EXTREM KINDGERECHTER PROMPT
                if st.session_state['modus'] == "lernen":
                    prompt = "Du bist ein herzlicher Vorlese-Freund. Erkläre die Aufgabe oder lies den Text sehr freundlich und motivierend vor. Sprich ein Kind (5 Jahre) direkt an. Max. 2-3 kurze Sätze."
                else:
                    prompt = "Du bist ein begeisterter Entdecker-Freund. Sag dem Kind, was für ein tolles Ding es gefunden hat und erkläre es ganz lieb. Max 2 Sätze."
                
                base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                # Stimme: 'shimmer' ist sehr freundlich/weiblich, 'alloy' ist neutral.
                audio_res = client.audio.speech.create(model="tts-1", voice="shimmer", input=res.choices[0].message.content)
                st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')

        if 'audio' in st.session_state:
            st.markdown('<div class="play-container"><div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                st.balloons()
            st.markdown('</div></div>', unsafe_allow_html=True)
