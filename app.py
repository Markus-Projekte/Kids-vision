import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="EMMA Kids Vision", page_icon="🐮")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Optimiert für die Rohr-Montage) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    .stButton > button { 
        border-radius: 25px !important; 
        height: 110px !important; 
        width: 100% !important;
        font-size: 26px !important;
        font-weight: bold !important;
        color: #5D4037 !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.1) !important;
    }
    .btn-audio button { background-color: #FFEB3B !important; border: 5px solid white !important; }
    .btn-back button { background-color: #FFCCBC !important; height: 60px !important; font-size: 18px !important; }
    .stCameraInput { border: 10px solid #5D4037 !important; border-radius: 30px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    try:
        response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
        return base64.b64encode(response.content).decode('utf-8')
    except:
        return None

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown("<h1 style='text-align:center;'>🐮 EMMA</h1>", unsafe_allow_html=True)
    if st.button("📚 BÜCHER LESEN"):
        st.session_state.update({"modus": "buch", "seite": "kamera", "show_audio": False})
        st.rerun()
    if st.button("🌍 WELT ENTDECKEN"):
        st.session_state.update({"modus": "welt", "seite": "kamera", "show_audio": False})
        st.rerun()

# --- 4. ANALYSE-SEITE ---
elif st.session_state['seite'] == 'kamera':
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK"):
        st.session_state.update({"seite": "start", "show_audio": False, "audio": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # WICHTIG: Audio-Button zeigen, sobald Daten da sind
    if st.session_state.get('show_audio') and st.session_state.get('audio'):
        st.markdown('<div class="btn-audio">', unsafe_allow_html=True)
        if st.button("🔊 EMMA ANHÖREN"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_hash') != img_hash:
            st.session_state.update({'last_hash': img_hash, 'show_audio': False, 'processing': True})
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut ganz genau hin..."):
            try:
                base_img = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
                p = "Lies den Text im Bild vor." if st.session_state['modus'] == "buch" else "Erkläre das Bild kindgerecht in 2 Sätzen." [cite: 17, 20]
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_img}"}}]}]
                )
                
                audio_data = get_emma_audio(res.choices[0].message.content) [cite: 22]
                if audio_data:
                    st.session_state.update({'audio': audio_data, 'show_audio': True, 'processing': False})
                    st.rerun()
            except Exception as e:
                st.session_state['processing'] = False
                st.info("Emma braucht einen Moment länger... bitte kurz warten.")
