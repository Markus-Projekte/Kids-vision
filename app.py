import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP (Einfach & Stabil) ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Prototyp-Design) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    .stButton > button { 
        border-radius: 20px !important; 
        border: 3px solid white !important; 
        height: 70px !important; 
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1) !important;
        margin-bottom: 10px;
        color: #5D4037 !important;
    }

    /* Farben */
    .btn-buch button { background-color: #BBDEFB !important; }
    .btn-welt button { background-color: #C8E6C9 !important; }
    .btn-back button { background-color: #FFCCBC !important; }
    .btn-play button { background-color: #FFF59D !important; }

    /* Zielrohr-Simulation (Brauner Rahmen) */
    .stCameraInput {
        border: 10px solid #5D4037 !important;
        border-radius: 25px !important;
        overflow: hidden;
    }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .finger { text-align: center; font-size: 50px; animation: bounce 1s infinite; }
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
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER ENTDECKEN", key="start_r"):
        st.session_state.update({"modus": "buch", "seite": "kamera"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "welt", "seite": "kamera"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK ZUM START", key="nav_back"):
        for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
            st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Audio-Button (Erscheint nur, wenn die Analyse fertig ist)
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
        if st.button("🔊 EMMA ANHÖREN", key="play_audio"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto") 
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['show_audio'] = False
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # Die bewährten Prompts [cite: 17, 20]
            if st.session_state['modus'] == "buch":
                prompt = "Du bist EMMA. Lies den Text im Bild präzise vor. Max 4 Sätze."
            else:
                prompt = "Du bist EMMA. Erkläre das Foto kindgerecht in 2 Sätzen."
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                audio_data = get_emma_audio(res.choices[0].message.content)
                if audio_data:
                    st.session_state['audio'] = audio_data
                    st.session_state['show_audio'] = True
                st.session_state['processing'] = False
                st.rerun()
            except:
                st.session_state['processing'] = False
                st.error("Fehler bei der Verbindung zu Emma.")
