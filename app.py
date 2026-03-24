import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision: EMMI", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. ZENTRIERTES & KOMPAKTES DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
    @keyframes swing { 0%, 100% { transform: rotate(-10deg); } 50% { transform: rotate(10deg); } }
    
    /* EMMI Sektion weit oben */
    .emmi-container {
        text-align: center;
        margin-top: -50px; /* Extrem weit nach oben */
        margin-bottom: 5px;
    }

    .emmi-icon { 
        font-size: 100px; 
        animation: bounce 2s infinite ease-in-out;
    }

    .emmi-label {
        font-size: 32px; 
        font-family: 'Arial Black', sans-serif; 
        color: #5D4037; /* Schönes Schokobraun */
        margin-top: -10px;
        letter-spacing: 3px;
    }

    /* ZENTRIERUNG DER BUTTONS */
    [data-testid="stHorizontalBlock"] { 
        display: flex !important; 
        flex-direction: row !important; 
        justify-content: center !important; /* Horizontale Zentrierung */
        align-items: center !important;
        gap: 15px !important;
        width: 100% !important;
    }
    
    [data-testid="stColumn"] {
        flex: 0 1 160px !important; /* Feste Breite für die Buttons damit sie nicht wandern */
        min-width: 140px !important;
    }
    
    .stButton > button { 
        width: 100% !important; 
        height: 150px !important; 
        border-radius: 40px !important; 
        border: 7px solid white !important; 
        box-shadow: 0px 6px 0px rgba(0,0,0,0.05); 
    }
    .stButton p { font-size: 70px !important; }
    
    .btn-lernen button { background-color: #B3E5FC !important; } 
    .btn-entdecken button { background-color: #C8E6C9 !important; } 

    /* Kamera-Seite Tweaks */
    .emmi-nav-swing { font-size: 60px; text-align: center; animation: swing 0.8s infinite ease-in-out; }
    .emmi-nav-static { font-size: 60px; text-align: center; }
    .back-btn button { height: 70px !important; width: 70px !important; font-size: 30px !important; background-color: #FFCCBC !important; border-radius: 18px !important; }
    .play-btn button { height: 75px !important; width: 75px !important; font-size: 45px !important; background-color: #FFF9C4 !important; border-radius: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'
if 'warten' not in st.session_state:
    st.session_state['warten'] = False

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emmi-container"><div class="emmi-icon">🐮</div><div class="emmi-label">EMMI</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚", key="btn_book"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍", key="btn_world"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SEITE 2: KAMERA-MODUS ---
elif st.session_state['seite'] == 'kamera':
    c_back, c_cow, c_play = st.columns([1, 1, 1])
    with c_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['warten'] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c_cow:
        if st.session_state['warten']:
            st.markdown('<div class="emmi-nav-swing">🐮</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="emmi-nav-static">🐮</div>', unsafe_allow_html=True)
    with c_play:
        if 'audio' in st.session_state and not st.session_state['warten']:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            st.session_state['warten'] = True 
            st.rerun() 

if st.session_state['seite'] == 'kamera' and st.session_state['warten']:
    with st.spinner(""):
        instruktion = """Du bist Kuh EMMI, eine schlaue Naturforscherin. 
        Erkläre dem Kind (5 Jahre) ganz genau, was du auf dem Foto siehst. 
        Nenne zuerst den Namen und erzähle dann einen spannenden, tollen Fakt dazu. 
        Benutze max. 3 kurze Sätze.""" if st.session_state['modus'] == "entdecken" else "Du bist Kuh EMMI. Hilf dem Kind liebevoll bei dieser Aufgabe."

        base64_image = base64.b64encode(st.session_state['last_img_bytes']).decode('utf-8')
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": instruktion},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}]
        )
        audio_res = client.audio.speech.create(model="tts-1", voice="alloy", input=res.choices[0].message.content)
        st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')
        st.session_state['warten'] = False 
        st.rerun()
