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

# --- 2. EMMI-DESIGN & ANIMATIONEN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
    @keyframes swing { 0%, 100% { transform: rotate(-12deg); } 50% { transform: rotate(12deg); } }
    
    .emmi-main { 
        font-size: 110px; 
        text-align: center; 
        margin-top: 10px; 
        animation: bounce 2s infinite ease-in-out;
    }

    .emmi-text {
        text-align: center; 
        font-size: 34px; 
        font-family: 'Comic Sans MS', cursive; 
        font-weight: bold;
        color: #5D4037;
        margin-bottom: 25px;
    }

    .emmi-nav-swing {
        font-size: 65px;
        text-align: center;
        animation: swing 0.8s infinite ease-in-out;
        margin-top: -10px;
    }
    
    .emmi-nav-static {
        font-size: 65px;
        text-align: center;
        margin-top: -10px;
    }

    /* Layout für engere Buttons */
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; justify-content: center !important; gap: 15px !important; padding: 0 5% !important; }
    [data-testid="stColumn"] { width: 45% !important; flex: 0 1 auto !important; }
    
    .stButton > button { width: 100% !important; height: 165px !important; border-radius: 40px !important; border: 8px solid white !important; box-shadow: 0px 8px 0px rgba(0,0,0,0.05); }
    .stButton p { font-size: 75px !important; }
    
    .btn-lernen button { background-color: #B3E5FC !important; } 
    .btn-entdecken button { background-color: #C8E6C9 !important; } 
    .back-btn button { height: 75px !important; width: 75px !important; font-size: 35px !important; background-color: #FFCCBC !important; border-radius: 20px !important; border: 4px solid white !important; }
    .play-btn button { height: 80px !important; width: 80px !important; font-size: 50px !important; background-color: #FFF9C4 !important; border-radius: 25px !important; border: 5px solid white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'
if 'warten' not in st.session_state:
    st.session_state['warten'] = False

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emmi-main">🐮</div>', unsafe_allow_html=True)
    st.markdown('<div class="emmi-text">Hallo! Ich bin EMMI!</div>', unsafe_allow_html=True)
    
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

    # Sobald ein Foto gemacht wurde
    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            st.session_state['warten'] = True 
            st.rerun() 

# Logik für KI-Verarbeitung (während EMMI schwingt)
if st.session_state['seite'] == 'kamera' and st.session_state['warten']:
    with st.spinner(""):
        if st.session_state['modus'] == "entdecken":
            instruktion = """Du bist Kuh EMMI, eine schlaue Naturforscherin. 
            Erkläre dem Kind (5 Jahre) ganz genau, was du auf dem Foto siehst. 
            Nenne zuerst den Namen und erzähle dann einen spannenden, tollen Fakt dazu. 
            Benutze max. 3 kurze Sätze."""
        else:
            instruktion = "Du bist Kuh EMMI. Hilf dem Kind liebevoll bei dieser Aufgabe."

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
