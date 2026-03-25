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

# --- 2. DESIGN & LAYOUT ---
bg_color = "#E3F2FD" if st.session_state.get('modus') == "entdeckungsreise" else "#FFF9C4"
secondary_bg = "#BBDEFB" if st.session_state.get('modus') == "entdeckungsreise" else "#FFFDE7"

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 100%); }}
    
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
    
    /* Buttons nebeneinander erzwingen */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
    }}

    .stButton > button {{ 
        border-radius: 25px !important; 
        border: 4px solid white !important; 
        height: 120px !important;
        width: 120px !important;
    }}
    .stButton p {{ font-size: 55px !important; }}
    
    /* Kamera Button & Finger */
    .stCameraInput button {{
        background-color: #A5D6A7 !important;
        color: white !important;
        border: 3px solid white !important;
        font-weight: bold !important;
    }}
    
    .finger-up {{
        text-align: center;
        font-size: 50px;
        animation: bounce 1s infinite;
        margin-top: -10px;
    }}
    
    .back-btn button {{ background-color: #FF7043 !important; height: 70px !important; width: 70px !important; }}
    .play-btn button {{ background-color: #FDD835 !important; height: 70px !important; width: 70px !important; }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

# --- 3. LOGIK ---
if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# RESET-FUNKTION
def reset_emma():
    for key in ['audio', 'last_img_hash', 'current_text']:
        if key in st.session_state: del st.session_state[key]

# --- 4. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; font-size:30px; font-weight:bold; color:#5D4037;">EMMA</div>', unsafe_allow_html=True)
    
    # Hier werden die Spalten für das "Nebeneinander" definiert
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚", key="b1"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Zeig mir dein Buch!")})
            st.rerun()
    with col2:
        if st.button("🌍", key="b2"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Was willst du mir zeigen?")})
            st.rerun()

# --- 5. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔙", key="back"):
            reset_emma()
            st.session_state.update({"seite": "start", "modus": "start"})
            st.rerun()
    with c2:
        if 'audio' in st.session_state:
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("")
    
    # Der Finger zeigt jetzt nach OBEN auf den Button
    st.markdown('<div class="finger-up">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Nur wenn das Bild NEU ist, wird die KI gefragt
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            with st.spinner(" "):
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = "Du bist EMMA. 1. Lies den Text vom Bild vor. 2. Wenn es Klappen im Buch gibt, frag das Kind danach. Max 3 Sätze."
                else:
                    prompt = "Du bist EMMA. Erkläre das Foto kindgerecht in max 2 Sätzen."
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
