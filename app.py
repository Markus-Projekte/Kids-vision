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

# --- 2. OPTIMIERTES DESIGN (MITTIG, KOMPAKT, KRÄFTIGE FARBEN) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    
    /* EMMA Container */
    .emma-container { text-align: center; margin-top: -30px; margin-bottom: 5px; }
    .emma-icon { font-size: 80px; animation: bounce 2s infinite ease-in-out; }
    .emma-label { font-size: 32px; font-family: 'Arial Black', sans-serif; color: #5D4037; margin-top: -5px; }

    /* Zentrierung & Button-Größe */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        justify-content: center !important; /* Zentriert die Spalten */
        gap: 15px !important;
        width: 100% !important;
    }
    
    [data-testid="stColumn"] {
        flex: 0 1 auto !important;
        min-width: 120px !important; /* Etwas schmaler als vorher */
    }
    
    .stButton > button { 
        border-radius: 30px !important; 
        border: 5px solid white !important; 
        box-shadow: 0px 4px 0px rgba(0,0,0,0.05);
        height: 120px !important; /* Kleiner als vorher */
        width: 120px !important;  /* Kleiner als vorher */
    }
    .stButton p { font-size: 55px !important; }
    
    /* Kräftigere Farben */
    .btn-lernen button { background-color: #29B6F6 !important; } /* Kräftiges Hellblau */
    .btn-entdecken button { background-color: #66BB6A !important; } /* Kräftiges Grün */
    .back-btn button { background-color: #FF8A65 !important; height: 60px !important; width: 60px !important; } /* Kräftigeres Orange */
    .play-btn button { background-color: #FFEE58 !important; height: 70px !important; width: 70px !important; } /* Kräftigeres Gelb */
    
    .stCameraInput label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktion für Audio mit Stimme 'NOVA'
def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    # Namensänderung auf EMMA
    st.markdown('<div class="emma-container"><div class="emma-icon">🐮</div><div class="emma-label">EMMA</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚", key="lernen_btn"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emma_audio("Hallo! Ich bin EMMA. Mach mir ein Foto!") # Gekürzter Begrüßungstext
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍", key="entdecken_btn"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emma_audio("Hallo! Ich bin EMMA. Mach mir ein Foto!") # Gekürzter Begrüßungstext
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SEITE 2: KAMERA ---
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
        st.markdown('<div style="font-size: 55px; text-align: center;">🐮</div>', unsafe_allow_html=True)
    with c3:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align: center; font-size: 40px; margin-bottom: 10px;">📸 ✨</div>', unsafe_allow_html=True)
    bild_datei = st.camera_input("")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner(" "): 
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                prompt = """Du bist die herzliche Kuh EMMA. Erkläre einem 5-jährigen Kind direkt, was auf dem Foto ist. 
                Regeln:
                1. KEINE Begrüßung, KEIN 'Ich sehe...', KEINE Vorstellung.
                2. Nenne sofort den Namen des Objekts.
                3. Ein kurzer, toller Fakt.
                4. Max. 2 Sätze. Ganz einfache Sprache."""

                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
