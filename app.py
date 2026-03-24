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

# --- 2. DAS "ERZWUNGENE" NEBENEINANDER DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFECB3 100%); }
    
    .magic-cow-main { font-size: 100px; text-align: center; margin-top: 10px; }

    /* ERZWINGT NEBENEINANDER AUF DEM HANDY */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }

    [data-testid="stColumn"] {
        width: 50% !important;
        flex: 1 1 auto !important;
    }

    /* BUTTON STYLING - Emojis wieder groß machen */
    .stButton > button {
        width: 100% !important;
        height: 180px !important; 
        border-radius: 30px !important;
        border: 8px solid white !important;
        box-shadow: 0px 10px 0px rgba(0,0,0,0.1);
    }
    
    /* Die Emojis im Button-Text ansprechen */
    .stButton p {
        font-size: 70px !important;
        line-height: 1 !important;
    }
    
    .btn-lernen button { background-color: #64B5F6 !important; }
    .btn-entdecken button { background-color: #81C784 !important; }

    /* NAVIGATION OBEN */
    .back-btn button { height: 70px !important; width: 70px !important; font-size: 35px !important; background-color: #FF8A65 !important; border-radius: 20px !important; }
    .play-btn button { height: 70px !important; width: 70px !important; font-size: 40px !important; background-color: #FFD54F !important; border-radius: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="magic-cow-main">🐮</div>', unsafe_allow_html=True)
    
    # Wir nutzen st.columns, aber unser CSS oben erzwingt das Nebeneinander
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
