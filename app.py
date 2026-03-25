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

# --- 2. CSS FÜR MOBILE NEBENEINANDER & DESIGN ---
bg_color = "#E3F2FD" if st.session_state.get('modus') == "entdeckungsreise" else "#FFF9C4"
secondary_bg = "#BBDEFB" if st.session_state.get('modus') == "entdeckungsreise" else "#FFFDE7"

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 100%); }}
    
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
    
    /* ERZWINGT NEBENEINANDER AUF DEM HANDY */
    [data-testid="column"] {{
        width: calc(50% - 10px) !important;
        flex: 1 1 calc(50% - 10px) !important;
        min-width: calc(50% - 10px) !important;
    }}
    
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
    }}

    .stButton > button {{ 
        border-radius: 25px !important; 
        border: 4px solid white !important; 
        height: 110px !important;
        width: 110px !important;
        background-color: white !important;
    }}
    .stButton p {{ font-size: 50px !important; }}
    
    .stCameraInput button {{
        background-color: #A5D6A7 !important;
        color: white !important;
        border: 3px solid white !important;
    }}
    
    .finger-up {{ text-align: center; font-size: 50px; animation: bounce 1s infinite; margin-top: -10px; }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; font-size:30px; font-weight:bold; margin-bottom:20px;">EMMA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚", key="btn_reise"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Zeig mir dein Buch!")})
            st.rerun()
    with col2:
        if st.button("🌍", key="btn_welt"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Was willst du mir zeigen?")})
            st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔙", key="back"):
            for k in ['audio', 'last_img_hash', 'processing']: st.session_state.pop(k, None)
            st.session_state.update({"seite": "start", "modus": "start"})
            st.rerun()
    with c2:
        # Lautsprecher nur zeigen, wenn NICHT gerade ein neues Bild geladen wird
        if 'audio' in st.session_state and not st.session_state.get('processing', False):
            if st.button("🔊", key="play"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("")
    st.markdown('<div class="finger-up">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            # Sofort altes Audio löschen und "Laden" markieren
            st.session_state['processing'] = True
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner(" "):
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = """Du bist EMMA. Deine wichtigste Aufgabe: 
                    1. Suche nach Text im Bild. Wenn Text da ist, LIES IHN KOMPLETT VOR.
                    2. Wenn du Laschen, Kerben oder Papierkanten siehst, frag am Ende lieb nach den Klappen. 
                    3. Wenn kein Text da ist, beschreibe das Bild für ein Kind. Max 3 Sätze."""
                else:
                    prompt = "Du bist EMMA. Erkläre das Foto einem 5-jährigen Kind in 2 Sätzen."
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.session_state['processing'] = False
                st.rerun()
