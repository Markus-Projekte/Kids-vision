import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP & KONFIGURATION ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. DYNAMISCHES DESIGN (CSS) ---
bg_color = "#E3F2FD" if st.session_state.get('modus') == "entdeckungsreise" else "#FFF9C4"
secondary_bg = "#BBDEFB" if st.session_state.get('modus') == "entdeckungsreise" else "#FFFDE7"

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 100%); }}
    
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
    
    /* Zwingt Buttons auf Mobile nebeneinander */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 10px !important;
    }}
    [data-testid="column"] {{
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }}

    .stButton > button {{ 
        border-radius: 25px !important; 
        border: 4px solid white !important; 
        height: 110px !important;
        width: 100% !important;
        max-width: 130px !important;
        background-color: white !important;
    }}
    .stButton p {{ font-size: 50px !important; }}
    
    /* Farben */
    .btn-reise button {{ background-color: #00B0FF !important; }} 
    .btn-welt button {{ background-color: #4CAF50 !important; }} 
    .back-btn button {{ background-color: #FF7043 !important; height: 65px !important; width: 65px !important; }}
    .play-btn button {{ background-color: #FDD835 !important; height: 65px !important; width: 65px !important; }}
    
    .stCameraInput button {{
        background-color: #A5D6A7 !important;
        color: white !important;
        border: 3px solid white !important;
    }}
    
    .finger-up {{ text-align: center; font-size: 50px; animation: bounce 1s infinite; margin-top: -10px; }}
    .waiting-emma {{ font-size: 80px; animation: bounce 1s infinite; text-align: center; margin: 20px; }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    # ÄNDERUNG: Stimme "shimmer" ist heller/kindgerechter, speed=0.85 ist langsamer
    response = client.audio.speech.create(
        model="tts-1", 
        voice="shimmer", 
        speed=0.85, 
        input=text
    )
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.session_state['modus'] = "start" 
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; font-size:25px; font-weight:bold; color:#5D4037; margin-bottom:20px;">EMMA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-reise">', unsafe_allow_html=True)
        if st.button("📚", key="r"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Ich bin Emma. Zeig mir dein Buch!")})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
        if st.button("🌍", key="w"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Ich bin Emma. Was hast du da?")})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙", key="b"):
            st.session_state.update({"seite": "start", "modus": "start"})
            for k in ['audio', 'last_img_hash', 'processing']: st.session_state.pop(k, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if 'audio' in st.session_state and not st.session_state.get('processing', False):
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊", key="p"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("")
    st.markdown('<div class="finger-up">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['processing'] = True
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner(" "):
                st.markdown('<div class="waiting-emma">🐮</div>', unsafe_allow_html=True)
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                safety = "SICHERHEIT: Falls Gewalt/Sexualität/Waffen, sag: 'Das möchte ich nicht sehen. Zeigst du mir was Schönes?'"
                
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = f"{safety} Du bist die liebe Kuh EMMA. 1. Lies den Text im Bild komplett vor. 2. Wenn du Klappen/Laschen siehst, frag lieb danach. 3. Max 3 Sätze."
                else:
                    prompt = f"{safety} Du bist die liebe Kuh EMMA. Erkläre das Foto für ein Kind (5J) in 2 sanften Sätzen."
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.session_state['processing'] = False
                st.rerun()
