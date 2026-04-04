import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision: Prototyp", page_icon="📸", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Optimiert für Hardware-Tests) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Großer, haptischer Button für den Prototyp */
    .stButton > button { 
        border-radius: 40px !important; 
        height: 80px !important; 
        font-size: 22px !important;
        font-weight: bold !important;
        background-color: #FFEB3B !important;
        border: 4px solid white !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2) !important;
        color: #5D4037 !important;
    }

    /* Simulation des Zielrohr-Ausschnitts */
    .stCameraInput {
        border: 12px solid #5D4037 !important;
        border-radius: 30px !important;
        overflow: hidden;
    }
    
    .diag-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border: 2px dashed #5D4037;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;">KIDS VISION PROTOTYP</h1>', unsafe_allow_html=True)
    
    if st.button("🚀 TEST-MODUS STARTEN", key="start_test"):
        st.session_state.update({"seite": "kamera", "welcome_audio": get_emma_audio("Prototyp bereit. Teste jetzt den Abstand!")})
        st.rerun()

# --- 4. DIAGNOSE- & KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔙", key="nav_b"):
            st.session_state['seite'] = 'start'
            st.rerun()
    
    # Audio-Button (erscheint nach Analyse)
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        if st.button("🔊 ANHÖREN", key="play_a"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Diagnose-Anzeige für dich
    st.markdown('<div class="diag-box"><b>Diagnose:</b> Bewege das Handy, bis der Text im Rahmen scharf und hell ist.</div>', unsafe_allow_html=True)
    
    bild_datei = st.camera_input("Ziel-Kamera") 
    
    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['show_audio'] = False
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("EMMA prüft Bildqualität..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # DIAGNOSE-PROMPT
            prompt = """Du bist EMMA und hilfst beim Testen eines Hardware-Geräts.
            1. Beurteile ZUERST kurz die Bildqualität (Licht, Schärfe). 
            2. Wenn das Bild schlecht ist, sag: 'Oh, ich brauche ein bisschen mehr Licht oder Ruhe für ein scharfes Bild!'
            3. Wenn das Bild gut ist, lies den Text vor oder erkläre das Objekt kindgerecht.
            Antworte kurz und präzise (max. 3 Sätze)."""
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.session_state['processing'] = False
                st.session_state['show_audio'] = True
                st.rerun()
            except:
                st.session_state['processing'] = False
                st.rerun()
