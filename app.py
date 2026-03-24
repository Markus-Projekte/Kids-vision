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

# --- 2. KINDERGERECHTES DESIGN (STABIL & MITTIG) ---
st.markdown("""
    <style>
    /* Hintergrund & Font */
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    /* EMMA Animation */
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .emma-container { text-align: center; padding-top: 20px; padding-bottom: 20px; }
    .emma-icon { font-size: 80px; animation: bounce 2s infinite ease-in-out; }
    .emma-label { font-size: 36px; font-family: 'Arial Black', sans-serif; color: #5D4037; }

    /* Button-Zentrierung für Mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 20px !important;
    }

    /* Kräftige, runde Buttons */
    .stButton > button { 
        border-radius: 35px !important; 
        border: 5px solid white !important; 
        box-shadow: 0px 6px 12px rgba(0,0,0,0.1);
        height: 130px !important;
        width: 130px !important;
        transition: transform 0.2s;
    }
    .stButton > button:active { transform: scale(0.95); }
    .stButton p { font-size: 60px !important; }
    
    /* Button Farben */
    .btn-lernen button { background-color: #00B0FF !important; } /* Leuchtendes Blau */
    .btn-entdecken button { background-color: #4CAF50 !important; } /* Kräftiges Grasgrün */
    .back-btn button { background-color: #FF7043 !important; height: 70px !important; width: 70px !important; }
    .play-btn button { background-color: #FDD835 !important; height: 80px !important; width: 80px !important; }
    
    /* Kamera Bereich sauber halten */
    .stCameraInput { margin-top: 20px; border-radius: 20px; overflow: hidden; }
    .stCameraInput label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktion für Audio (Weich & Herzlich)
def get_emma_audio(text):
    # Wir nutzen 'nova', geben ihr aber via Text-Prompt mehr 'Gefühl'
    response = client.audio.speech.create(
        model="tts-1", 
        voice="nova", 
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
            # Weichere Formulierung
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
        st.markdown('<div style="font-size: 60px; text-align: center; margin-top: 10px;">🐮</div>', unsafe_allow_html=True)
    with c3:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align: center; font-size: 40px; margin-top: 10px;">📸 ✨</div>', unsafe_allow_html=True)
    
    # Kamera Input - Ohne CSS-Tricks drumherum für maximale Stabilität
    bild_datei = st.camera_input("")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner(" "): 
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                prompt = """Du bist EMMA, eine ganz liebe Kuh. Erkläre einem 5-jährigen Kind 
                ganz sanft und langsam, was auf dem Foto ist. 
                Nenne zuerst den Namen des Objekts und dann einen lieben, kurzen Fakt. 
                Benutze einfache Worte. Max. 2 Sätze."""

                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
