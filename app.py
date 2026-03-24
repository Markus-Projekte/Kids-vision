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

# --- 2. DAS PASTEL-DESIGN (ENGER ZUSAMMEN) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    .magic-cow-main { font-size: 100px; text-align: center; margin-top: 10px; }

    /* ERZWINGT ENGERES NEBENEINANDER */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important; /* Zentriert die Gruppe */
        gap: 20px !important; /* Geringerer Abstand zwischen den Buttons */
        padding: 0 10% !important; /* Schiebt sie von den Rändern weg zur Mitte */
    }

    [data-testid="stColumn"] {
        width: 40% !important; /* Spalten etwas schmaler für engeren Look */
        flex: 0 1 auto !important;
    }

    /* BUTTON STYLING - Weiche Farben */
    .stButton > button {
        width: 100% !important;
        height: 160px !important; 
        border-radius: 40px !important;
        border: 6px solid white !important;
        box-shadow: 0px 8px 0px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    .stButton p { font-size: 70px !important; }
    
    /* Sanfte Pastelltöne */
    .btn-lernen button { background-color: #B3E5FC !important; } /* Sanftes Blau */
    .btn-entdecken button { background-color: #C8E6C9 !important; } /* Sanftes Grün */

    /* NAVIGATION OBEN */
    .back-btn button { 
        height: 70px !important; 
        width: 70px !important; 
        font-size: 35px !important; 
        background-color: #FFCCBC !important; /* Pastell-Orange */
        border-radius: 20px !important; 
        border: 4px solid white !important;
    }
    
    .play-btn button { 
        height: 70px !important; 
        width: 70px !important; 
        font-size: 40px !important; 
        background-color: #FFF9C4 !important; /* Pastell-Gelb */
        border-radius: 20px !important; 
        border: 4px solid white !important;
    }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="magic-cow-main">🐮</div>', unsafe_allow_html=True)
    
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

# --- 4. KAMERA-MODUS ---
elif st.session_state['seite'] == 'kamera':
    c_back, c_cow, c_play = st.columns([1, 1, 1])
    with c_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c_cow:
        st.markdown('<div style="font-size: 50px; text-align: center;">🐮</div>', unsafe_allow_html=True)
    with c_play:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        if 'audio' not in st.session_state or st.session_state.get('last_img_bytes') != bild_datei.getvalue():
            st.session_state['last_img_bytes'] = bild_datei.getvalue()
            with st.spinner(" "):
                base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Du bist eine liebe Kuh. Erkläre kurz (2 Sätze) für ein Kind, was du siehst."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                audio_res = client.audio.speech.create(model="tts-1", voice="alloy", input=res.choices[0].message.content)
                st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')
                st.rerun()
