import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP (Basierend auf stabiler Version) ---
st.set_page_config(page_title="EMMA Kids Vision", page_icon="🐮")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Fokus auf Stabilität & Rohr-Bedienung) ---
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
        margin-bottom: 10px;
    }
    /* Farbleitsystem */
    .btn-buch button { background-color: #BBDEFB !important; }
    .btn-welt button { background-color: #C8E6C9 !important; }
    .btn-story button { background-color: #E1BEE7 !important; }
    .btn-audio button { background-color: #FFEB3B !important; border: 5px solid white !important; height: 120px !important; font-size: 28px !important; }
    .btn-back button { background-color: #FFCCBC !important; height: 50px !important; font-size: 16px !important; }
    
    .stCameraInput { border: 8px solid #5D4037 !important; border-radius: 25px !important; }
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
    st.markdown("<h1 style='text-align:center; color:#5D4037;'>🐮 EMMA</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER LESEN"):
        st.session_state.update({"modus": "buch", "seite": "kamera", "audio": None, "last_hash": None})
        st.rerun()
    st.markdown('</div><div class="btn-welt">', unsafe_allow_html=True)
    
    if st.button("🌍 WELT ENTDECKEN"):
        st.session_state.update({"modus": "welt", "seite": "kamera", "audio": None, "last_hash": None})
        st.rerun()
    st.markdown('</div><div class="btn-story">', unsafe_allow_html=True)
    
    if st.button("✨ GESCHICHTEN-ZAUBER"):
        st.session_state.update({"modus": "story", "seite": "kamera", "audio": None, "last_hash": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
        
        if st.session_state.get('last_hash') != img_hash:
            with st.spinner("Emma schaut hin..."):
                try:
                    base_img = base64.b64encode(img_bytes).decode('utf-8')
                    
                    # KI-Anweisungen (Prompts) [cite: 17, 18, 19, 20]
                    if st.session_state['modus'] == "buch":
                        p = "Du bist EMMA. Lies den Text im Bild präzise vor. Max 4 Sätze."
                    elif st.session_state['modus'] == "welt":
                        p = "Du bist EMMA. Erkläre das Foto kindgerecht in 2 Sätzen."
                    else: # Geschichten-Zauber
                        p = "Du bist EMMA. Erkenne die Figur oder das Spielzeug und erzähle eine kurze, liebevolle Geschichte dazu (6-8 Sätze). Wenn es Marshall von PAW Patrol ist, erwähne seine Freunde."
                    
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_img}"}}]}]
                    )
                    
                    audio_data = get_emma_audio(res.choices[0].message.content)
                    if audio_data:
                        st.session_state.update({'audio': audio_data, 'last_hash': img_hash})
                except:
                    st.warning("Emma braucht kurz Pause. Bitte nochmal probieren.")

    if st.session_state.get('audio'):
        st.markdown('<div class="btn-audio" style="margin-top:20px;">', unsafe_allow_html=True)
        if st.button("🔊 ANHÖREN"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
