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

# --- 2. STYLING (Mix aus Design und Hardware-Test) ---
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

    .btn-buch button { background-color: #BBDEFB !important; }
    .btn-welt button { background-color: #C8E6C9 !important; }
    .btn-back button { background-color: #FFCCBC !important; }
    .btn-play button { background-color: #FFF59D !important; }

    /* Zielrohr-Simulation */
    .stCameraInput {
        border: 8px solid #5D4037 !important;
        border-radius: 25px !important;
        overflow: hidden;
    }
    
    .diag-hint {
        text-align: center;
        font-size: 14px;
        color: #5D4037;
        background: white;
        padding: 5px;
        border-radius: 10px;
        margin-bottom: 10px;
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
    st.markdown('<h1 style="text-align:center;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER ENTDECKEN", key="start_r"):
        st.session_state.update({"modus": "buch", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "welt", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Was willst du mir zeigen?")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA- & ANALYSE-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK", key="nav_back"):
        st.session_state.update({"seite": "start", "show_audio": False})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
        if st.button("🔊 ANHÖREN", key="play_audio"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="diag-hint">Abstand halten & stillhalten für EMMA...</div>', unsafe_allow_html=True)
    bild_datei = st.camera_input("Kamera") 

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state.update({'show_audio': False, 'last_img_hash': img_hash, 'processing': True})
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut ganz genau hin..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # KOMBINIERTER PROMPT (Diagnose + Inhalt)
            if st.session_state['modus'] == "buch":
                prompt = """Du bist EMMA. Deine Aufgabe: 
                1. Prüfe kurz die Bildqualität. Wenn es zu dunkel/unscharf ist, sag es lieb.
                2. Wenn das Bild gut ist, LIES DEN TEXT im Bild präzise vor.
                3. Erwähne Klappen nur, wenn du sie sicher siehst. Max 4 Sätze.""" [cite: 17, 18, 19]
            else:
                prompt = """Du bist EMMA. Deine Aufgabe:
                1. Prüfe die Bildqualität.
                2. Wenn gut: Erkenne das Objekt (Pflanze, Tier, Ding) und erkläre es kindgerecht.
                Nenne den Namen des Objekts! Max 2 Sätze.""" [cite: 20]
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content) [cite: 22]
                st.session_state['processing'] = False
                st.session_state['show_audio'] = True
                st.rerun()
            except:
                st.session_state['processing'] = False
                st.rerun()
