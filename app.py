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
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
    .waiting-emma { font-size: 80px; animation: bounce 1s infinite ease-in-out; text-align: center; margin: 20px; }
    .emma-container { text-align: center; padding: 10px; }
    .emma-icon { font-size: 70px; animation: bounce 2s infinite ease-in-out; }
    .emma-label { font-size: 30px; font-family: 'Arial Black', sans-serif; color: #5D4037; }
    [data-testid="stHorizontalBlock"] { display: flex !important; justify-content: center !important; gap: 15px !important; }
    .stButton > button { border-radius: 30px !important; border: 4px solid white !important; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); height: 120px !important; width: 120px !important; }
    .stButton p { font-size: 55px !important; }
    .btn-lernen button { background-color: #00B0FF !important; } 
    .btn-entdecken button { background-color: #4CAF50 !important; } 
    .back-btn button { background-color: #FF7043 !important; height: 60px !important; width: 60px !important; }
    .play-btn button { background-color: #FDD835 !important; height: 70px !important; width: 70px !important; }
    .stCameraInput label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(
        model="tts-1", 
        voice="nova", 
        speed=0.9, # Etwas schneller als zuvor
        input=text
    )
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emma-container"><div class="emma-icon">🐮</div><div class="emma-label">EMMA</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚", key="lernen_btn"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emma_audio("Schau mal, ich bin EMMA! Magst du mir ein Foto machen?")
            st.session_state['welcome_played'] = False # Merker setzen
            st.rerun()
    with col2:
        if st.button("🌍", key="entdecken_btn"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emma_audio("Schau mal, ich bin EMMA! Magst du mir ein Foto machen?")
            st.session_state['welcome_played'] = False # Merker setzen
            st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    # Begrüßung nur abspielen, wenn sie in dieser Session noch nicht lief
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True # Verhindert doppeltes Abspielen bei Neuladen

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("🔙", key="back"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
    with c2:
        st.markdown('<div style="font-size: 50px; text-align: center;">🐮</div>', unsafe_allow_html=True)
    with c3:
        if 'audio' in st.session_state:
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            with st.spinner(" "): 
                st.markdown('<div class="waiting-emma">🐮</div>', unsafe_allow_html=True)
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                prompt = "Du bist die herzliche Kuh EMMA. Erkläre einem Kind sanft, was auf dem Foto ist. Name zuerst, dann ein Fakt. Max. 2 Sätze."
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
