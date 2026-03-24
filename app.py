import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision: EMMI", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. KINDERGERECHTES DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    
    .emmi-container { text-align: center; margin-top: -20px; margin-bottom: 5px; }
    .emmi-icon { font-size: 80px; animation: bounce 2s infinite ease-in-out; }
    .emmi-label { font-size: 32px; font-family: 'Arial Black', sans-serif; color: #5D4037; margin-top: -5px; }

    .camera-instruction { text-align: center; font-size: 45px; margin-bottom: 10px; }

    [data-testid="stHorizontalBlock"] { display: flex !important; justify-content: center !important; gap: 20px !important; }
    
    .stButton > button { 
        border-radius: 35px !important; 
        border: 6px solid white !important; 
        box-shadow: 0px 5px 0px rgba(0,0,0,0.05);
        height: 150px !important;
        width: 150px !important;
    }
    .stButton p { font-size: 70px !important; }
    
    .btn-lernen button { background-color: #B3E5FC !important; } 
    .btn-entdecken button { background-color: #C8E6C9 !important; } 
    .back-btn button { background-color: #FFCCBC !important; height: 65px !important; width: 65px !important; }
    .play-btn button { background-color: #FFF9C4 !important; height: 80px !important; width: 80px !important; }
    
    .stCameraInput label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktion für Audio mit NEUER STIMME 'NOVA'
def get_emmi_audio(text):
    # --- ÄNDERUNG: voice="nova" für eine lebendige, herzliche Frauenstimme ---
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emmi-container"><div class="emmi-icon">🐮</div><div class="emmi-label">EMMI</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚", key="lernen_btn"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emmi_audio("Hallo! Ich bin EMMI. Mach schnell ein Foto für mich!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍", key="entdecken_btn"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.session_state['audio_welcome'] = get_emmi_audio("Hallo! Ich bin EMMI. Mach schnell ein Foto für mich!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SEITE 2: KAMERA ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['audio_welcome']

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙", key="back"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="font-size: 55px; text-align: center;">🐮</div>', unsafe_allow_html=True)
    with c3:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="camera-instruction">📸 ✨</div>', unsafe_allow_html=True)
    bild_datei = st.camera_input("")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner(" "): 
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # --- NOCH STRIKTERE ANWEISUNG FÜR KURZE ANTWORTEN ---
                prompt = """Du bist eine herzliche Kuh. Erkläre einem 5-jährigen Kind direkt, was auf dem Foto ist. 
                Regeln:
                1. KEINE Begrüßung, KEIN 'Ich sehe...', KEINE Vorstellung.
                2. Nenne sofort den Namen des Objekts.
                3. Ein kurzer, toller Fakt.
                4. Max. 2 Sätze. Ganz einfache Sprache."""

                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                st.session_state['audio'] = get_emmi_audio(res.choices[0].message.content)
                st.rerun()
