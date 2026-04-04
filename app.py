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

# --- 2. STYLING (Basierend auf deinem Code [cite: 1, 2, 3, 4]) ---
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
    .stCameraInput { border: 8px solid #5D4037 !important; border-radius: 25px !important; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

# Initialisierung der Zustände [cite: 13]
if 'seite' not in st.session_state: st.session_state['seite'] = 'start'
if 'autoplay' not in st.session_state: st.session_state['autoplay'] = False

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER ENTDECKEN", key="start_r"):
        st.session_state.update({"modus": "buch", "seite": "kamera", "audio": get_emma_audio("Hallo! Zeig mir dein Buch!"), "autoplay": True})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "welt", "seite": "kamera", "audio": get_emma_audio("Hallo! Was willst du mir zeigen?"), "autoplay": True})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA- & ANALYSE-SEITE ---
elif st.session_state['seite'] == 'kamera':
    # Automatisches Abspielen, falls neues Audio vorhanden ist
    if st.session_state.get('autoplay') and 'audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['autoplay'] = False

    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK", key="nav_back"):
        for k in ['audio', 'last_img_hash', 'processing', 'autoplay']: 
            st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Manueller Abspiel-Button [cite: 14]
    if 'audio' in st.session_state:
        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
        if st.button("🔊 NOCHMAL HÖREN", key="play_audio"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Kamera") 

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state.update({'last_img_hash': img_hash, 'processing': True, 'autoplay': False})
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut ganz genau hin..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # Die Anweisungen für die KI (Prompts) [cite: 17, 18, 19, 20]
            if st.session_state['modus'] == "buch":
                p_text = "Du bist EMMA. Prüfe die Bildqualität. Wenn gut, lies den Text im Bild präzise vor. Erwähne Klappen nur, wenn du sie sicher siehst. Max 4 Sätze."
            else:
                p_text = "Du bist EMMA. Prüfe die Bildqualität. Wenn gut: Erkenne das Objekt und erkläre es kindgerecht. Nenne den Namen des Objekts! Max 2 Sätze."
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": p_text}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.session_state['processing'] = False
                st.session_state['autoplay'] = True # Aktiviert das automatische Abspielen nach dem Rerun
                st.rerun()
            except Exception as e:
                st.error("Fehler bei der Analyse.")
                st.session_state['processing'] = False
