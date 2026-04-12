import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="EMMA Prototyp", page_icon="🐮")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Große Buttons für das Rohr) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    .stButton > button { 
        border-radius: 20px !important; 
        height: 90px !important; 
        width: 100% !important;
        font-size: 22px !important;
        font-weight: bold !important;
        color: #5D4037 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
    }
    .btn-audio button { background-color: #FFEB3B !important; border: 4px solid white !important; }
    .btn-back button { background-color: #FFCCBC !important; height: 50px !important; font-size: 16px !important; }
    .stCameraInput { border: 8px solid #5D4037 !important; border-radius: 25px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    try:
        response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
        return base64.b64encode(response.content).decode('utf-8')
    except Exception:
        return None

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown("<h1 style='text-align:center;'>🐮 EMMA</h1>", unsafe_allow_html=True)
    if st.button("📚 BÜCHER LESEN"):
        st.session_state.update({"modus": "buch", "seite": "kamera", "audio": None, "last_hash": None})
        st.rerun()
    if st.button("🌍 WELT ENTDECKEN"):
        st.session_state.update({"modus": "welt", "seite": "kamera", "audio": None, "last_hash": None})
        st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK"):
        st.session_state.update({"seite": "start", "audio": None, "last_hash": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto machen")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Verarbeitung starten, wenn neues Bild
        if st.session_state.get('last_hash') != img_hash:
            with st.spinner("Emma schaut durch das Rohr..."):
                try:
                    base_img = base64.b64encode(img_bytes).decode('utf-8')
                    p = "Lies den Text im Bild genau vor." if st.session_state['modus'] == "buch" else "Erkläre das Foto in 2 Sätzen für ein Kind."
                    
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_img}"}}]}]
                    )
                    
                    audio_b64 = get_emma_audio(res.choices[0].message.content)
                    if audio_b64:
                        st.session_state['audio'] = audio_b64
                        st.session_state['last_hash'] = img_hash
                        # Kein Rerun hier, wir lassen die Anzeige direkt folgen
                except Exception:
                    st.warning("Verbindung hakt kurz... Bitte nochmal probieren.")

    # Der Audio-Button erscheint SOFORT hier unten, wenn st.session_state['audio'] gefüllt ist
    if st.session_state.get('audio'):
        st.markdown('<div class="btn-audio" style="margin-top:20px;">', unsafe_allow_html=True)
        if st.button("🔊 EMMA ANHÖREN"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
