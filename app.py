import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP (Stabil & Einfach) ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="📸", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Bitte API-Key in den Secrets hinterlegen!")
    st.stop()

# --- 2. STYLING (Dein Zielrohr-Design) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Großer Button für Kinderhände */
    .stButton > button { 
        border-radius: 30px !important; 
        height: 80px !important; 
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        background-color: #FFF59D !important;
        border: 4px solid white !important;
        color: #5D4037 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
    }

    /* Simulation des Hardware-Rohrs */
    .stCameraInput {
        border: 10px solid #5D4037 !important;
        border-radius: 25px !important;
    }
    
    .instruction {
        text-align: center;
        font-weight: bold;
        color: #5D4037;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    try:
        response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
        return base64.b64encode(response.content).decode('utf-8')
    except:
        return None

# --- 3. HAUPTSEITE ---
st.markdown('<div style="text-align:center; font-size:60px;">🐮</div>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center; color:#5D4037;">KIDS VISION</h1>', unsafe_allow_html=True)

# Anzeige der Audio-Antwort (Falls vorhanden)
if "audio_ready" in st.session_state:
    st.markdown('<div class="instruction">Emma ist bereit! 👇</div>', unsafe_allow_html=True)
    if st.button("🔊 EMMA ANHÖREN"):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_ready"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown('<div class="instruction">Schau durch das Zielrohr:</div>', unsafe_allow_html=True)
bild_datei = st.camera_input("Kamera")

# --- 4. LOGIK (Der einfache Weg) ---
if bild_datei:
    # Wir prüfen, ob es ein neues Bild ist
    img_bytes = bild_datei.getvalue()
    img_hash = hashlib.md5(img_bytes).hexdigest()
    
    if st.session_state.get('last_hash') != img_hash:
        with st.spinner("Emma schaut ganz genau hin..."):
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            
            # Der bewährte Prompt vom Vormittag
            prompt = "Du bist EMMA. Erkläre dieses Foto für ein Kind in 2 bis 3 Sätzen. Wenn Text da ist, lies ihn vor."
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                # Audio erstellen
                audio_base64 = get_emma_audio(res.choices[0].message.content)
                
                # Speichern und Seite neu laden
                st.session_state['audio_ready'] = audio_base64
                st.session_state['last_hash'] = img_hash
                st.rerun()
                
            except Exception as e:
                st.error(f"Oh weh, Emma hat einen Fehler: {e}")
