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

# --- 2. STYLING (ROBUST FÜR MOBILE) ---
bg_color = "#E3F2FD" if st.session_state.get('modus') == "entdeckungsreise" else "#FFF9C4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    
    /* Container für Buttons nebeneinander */
    .button-row {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }}

    .stButton > button {{ 
        border-radius: 20px !important; 
        border: 4px solid white !important; 
        height: 120px !important;
        width: 120px !important;
        font-size: 50px !important;
        background-color: white !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}
    
    .stCameraInput button {{
        background-color: #A5D6A7 !important;
        color: white !important;
        border: 2px solid white !important;
    }}

    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
    .emma-head {{ font-size: 80px; text-align: center; animation: bounce 2s infinite; }}
    .finger {{ font-size: 50px; text-align: center; animation: bounce 1s infinite; }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    # Sanfte Kinder/Frauenstimme, etwas langsamer
    response = client.audio.speech.create(model="tts-1", voice="shimmer", speed=0.85, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emma-head">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037;">EMMA</h1>', unsafe_allow_html=True)
    
    # Wir nutzen hier keine Columns mehr, sondern pures HTML für die Anordnung
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚", key="btn_r"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Muh! Hallo, ich bin Emma. Zeig mir dein Buch!")})
            st.rerun()
    with col2:
        if st.button("🌍", key="btn_w"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Muh! Ich bin Emma. Was hast du Schönes für mich?")})
            st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    # Willkommens-Audio
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    # Obere Buttons (Zurück & Play)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔙", key="back"):
            st.session_state.update({"seite": "start"})
            for k in ['audio', 'last_img_hash', 'processing']: st.session_state.pop(k, None)
            st.rerun()
    with c2:
        if 'audio' in st.session_state and not st.session_state.get('processing', False):
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Kamera
    bild_datei = st.camera_input("Kamera")
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['processing'] = True
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner("Emma denkt nach..."):
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = "Du bist EMMA, eine liebe Kuh. Lies den Text im Bild für ein Kind vor. Wenn du Klappen im Buch siehst, frag danach. Max 3 Sätze. Starte mit einem freundlichen Muh!"
                else:
                    prompt = "Du bist EMMA, eine liebe Kuh. Erkläre das Bild für ein 5-jähriges Kind. Max 2 Sätze. Starte mit einem freundlichen Muh!"
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                
                text_antwort = res.choices[0].message.content
                st.session_state['audio'] = get_emma_audio(text_antwort)
                st.session_state['processing'] = False
                st.rerun()
