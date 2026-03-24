import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. DAS DESIGN (MITTIG & INTERAKTIV) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    /* Hüpf-Animation für Wartezeit */
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
    .waiting-emma { font-size: 100px; animation: bounce 1s infinite ease-in-out; text-align: center; margin-top: 20px; }
    
    .emma-container { text-align: center; padding-top: 10px; }
    .emma-icon { font-size: 80px; animation: bounce 2s infinite ease-in-out; }
    .emma-label { font-size: 36px; font-family: 'Arial Black', sans-serif; color: #5D4037; }

    /* Fixe Zentrierung der Buttons auf Startseite */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 20px !important;
        padding-top: 20px;
    }

    /* Kompakte, kräftige Buttons */
    .stButton > button { 
        border-radius: 35px !important; 
        border: 5px solid white !important; 
        box-shadow: 0px 6px 12px rgba(0,0,0,0.1);
        height: 125px !important;
        width: 125px !important;
    }
    .stButton p { font-size: 60px !important; }
    
    /* Farben */
    .btn-lernen button { background-color: #00B0FF !important; } 
    .btn-entdecken button { background-color: #4CAF50 !important; } 
    .back-btn button { background-color: #FF7043 !important; height: 65px !important; width: 65px !important; }
    .play-btn button { background-color: #FDD835 !important; height: 80px !important; width: 80px !important; }
    
    /* Kamera Bereich ohne störendes CSS */
    .stCameraInput label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    # Nova Stimme: Langsam (0.85) für Kinder
    response = client.audio.speech.create(
        model="tts-1", 
        voice="nova", 
        speed=0.85, 
        input=text
    )
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emma-container"><div class="emma-icon">🐮</div><div class="emma-label">EMMA</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚", key="lernen_btn"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emma_audio("Schau mal, ich bin EMMA! Magst du mir ein Foto machen?")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍", key="entdecken_btn"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emma_audio("Schau mal, ich bin EMMA! Magst du mir ein Foto machen?")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SEITE 2: KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['audio_welcome']

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙", key="back"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="font-size: 60px; text-align: center;">🐮</div>', unsafe_allow_html=True)
    with c3:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            
            # Die hüpfende EMMA während der Wartezeit
            placeholder = st.empty()
            with placeholder.container():
                st.markdown('<div class="waiting-emma">🐮</div>', unsafe_allow_html=True)
                
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                prompt = "Du bist EMMA, eine ganz liebe Kuh. Erkläre einem 5-jährigen Kind ganz sanft, was auf dem Foto ist. Nenne zuerst den Namen und dann einen kurzen Fakt. Max. 2 Sätze."

                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                placeholder.empty() # Entfernt die hüpfende Kuh nach dem Laden
                st.rerun()
