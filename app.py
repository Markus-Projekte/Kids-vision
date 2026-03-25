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

# --- 2. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Buttons optimiert */
    .stButton > button { 
        border-radius: 20px !important; 
        border: 4px solid white !important; 
        height: 100px !important;
        width: 100% !important;
        font-size: 45px !important; /* Symbole schön groß */
        background-color: white !important;
    }
    
    .stCameraInput button {
        background-color: #A5D6A7 !important;
        color: white !important;
        font-size: 20px !important;
    }

    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .finger { text-align: center; font-size: 50px; animation: bounce 1s infinite; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;">EMMA</h1>', unsafe_allow_html=True)
    
    if st.button("📚", key="start_reise"): # Nur Symbol für Kinder
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
        
    if st.button("🌍", key="start_dinge"): # Nur Symbol für Kinder
        st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Was hast du da?")})
        st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    # Layout-Reihe für Steuerung
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙", key="nav_back"): # Nur der Pfeil
            for k in ['audio', 'last_img_hash', 'processing']: 
                if k in st.session_state: del st.session_state[k]
            st.session_state['seite'] = 'start'
            st.rerun()
    
    with col2:
        # Der Button erscheint NUR, wenn ein fertiges Audio da ist 
        # UND gerade kein neues Bild verarbeitet wird
        if 'audio' in st.session_state and not st.session_state.get('processing', False):
            if st.button("🔊", key="play_audio"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("📸") # Kamera-Icon
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Sobald ein neues Foto erkannt wird:
        if st.session_state.get('last_img_hash') != img_hash:
            # KRITISCH: Alles alte sofort löschen, damit der Lautsprecher verschwindet!
            st.session_state['processing'] = True
            if 'audio' in st.session_state:
                del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            st.rerun() # Seite neu laden, damit der Lautsprecher-Button sofort weg ist

    # Wenn ein Bild da ist, aber noch kein Audio generiert wurde (nach dem rerun)
    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            p = "Du bist EMMA. Erkläre das Bild für ein Kind in 2 Sätzen."
            if st.session_state['modus'] == "entdeckungsreise":
                p = "Du bist EMMA. Lies den Text vor und frage nach Klappen. Max 3 Sätze."
            
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": p},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}]
            )
            
            st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
            st.session_state['processing'] = False
            st.rerun()
