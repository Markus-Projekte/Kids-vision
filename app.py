import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="EMMA Kids Vision", page_icon="🐮")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Bitte API-Key hinterlegen!")
    st.stop()

# --- 2. HARDWARE-STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Buttons für die Rohr-Montage optimiert */
    .stButton > button { 
        border-radius: 25px !important; 
        height: 100px !important; 
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.1) !important;
        margin-bottom: 15px;
    }

    .btn-start { background-color: #BBDEFB !important; color: #5D4037 !important; } /* Blau */
    .btn-welt { background-color: #C8E6C9 !important; color: #5D4037 !important; } /* Grün */
    .btn-audio { background-color: #FFEB3B !important; color: #5D4037 !important; border: 5px solid white !important; }
    
    /* Kamera-Rahmen (Dein Rohr-Ausschnitt) */
    .stCameraInput { border: 10px solid #5D4037 !important; border-radius: 30px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE (Modus-Wahl) ---
if st.session_state['seite'] == 'start':
    st.markdown("<h1 style='text-align:center; color:#5D4037;'>🐮 EMMA</h1>", unsafe_allow_html=True)
    
    if st.button("📚 BÜCHER LESEN"):
        st.session_state.update({"modus": "buch", "seite": "kamera"})
        st.rerun()
    
    if st.button("🌍 WELT ENTDECKEN"):
        st.session_state.update({"modus": "welt", "seite": "kamera"})
        st.rerun()

# --- 4. ANALYSE-SEITE (Rohr-Betrieb) ---
elif st.session_state['seite'] == 'kamera':
    if st.button("🔙 ZURÜCK"):
        st.session_state.update({"seite": "start", "show_audio": False})
        st.rerun()

    # Großer Audio-Button, falls Emma fertig ist
    if st.session_state.get('show_audio'):
        if st.button("🔊 EMMA ANHÖREN", key="play"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Kamera-Interface
    bild_datei = st.camera_input("Foto machen")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_hash') != img_hash:
            with st.spinner("Emma schaut durch das Rohr..."):
                base_img = base64.b64encode(img_bytes).decode('utf-8')
                
                # Der "perfekte" Prompt für deine Hardware
                if st.session_state['modus'] == "buch":
                    prompt = "Lies den Text im Bild präzise vor. Wenn es zu dunkel ist, sag: 'Ich brauche mehr Licht im Rohr!'"
                else:
                    prompt = "Erkläre das Objekt im Bild kindgerecht in 2-3 Sätzen."

                try:
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_img}"}}
                        ]}]
                    )
                    st.session_state.update({
                        'audio': get_emma_audio(res.choices[0].message.content),
                        'show_audio': True,
                        'last_hash': img_hash
                    })
                    st.rerun()
                except:
                    st.error("Emma hat gerade keine Verbindung.")
