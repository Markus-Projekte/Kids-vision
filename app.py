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

# --- 2. DESIGN & STYLING ---
if st.session_state.get('modus') == "entdeckungsreise":
    bg_color = "#E3F2FD"
    secondary_bg = "#BBDEFB"
else:
    bg_color = "#FFF9C4"
    secondary_bg = "#FFFDE7"

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 100%); }}
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
    .waiting-emma {{ font-size: 80px; animation: bounce 1s infinite ease-in-out; text-align: center; margin: 20px; }}
    .emma-container {{ text-align: center; padding: 5px; margin-bottom: -10px; }}
    .emma-icon {{ font-size: 60px; animation: bounce 2s infinite ease-in-out; }}
    .emma-label {{ font-size: 25px; font-family: 'Arial Black', sans-serif; color: #5D4037; }}
    
    /* Layout Fix für Buttons nebeneinander */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
        width: 100% !important;
    }}
    .stButton > button {{ 
        border-radius: 30px !important; 
        border: 4px solid white !important; 
        height: 110px !important;
        width: 110px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    .stButton p {{ font-size: 50px !important; }}
    .btn-reise button {{ background-color: #00B0FF !important; }} 
    .btn-dinge button {{ background-color: #4CAF50 !important; }} 
    .back-btn button {{ background-color: #FF7043 !important; height: 60px !important; width: 60px !important; }}
    .play-btn button {{ background-color: #FDD835 !important; height: 60px !important; width: 60px !important; }}
    
    /* Kamera Styling */
    .stCameraInput {{ border-radius: 15px; overflow: hidden; }}
    .stCameraInput label {{ display: none !important; }}
    .stCameraInput button {{
        background-color: #A5D6A7 !important;
        color: white !important;
        border: 3px solid white !important;
        font-weight: bold !important;
    }}
    .click-here {{ text-align: center; font-size: 40px; animation: bounce 1s infinite; margin-top: 5px; }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.session_state['modus'] = "start" 
    st.markdown('<div class="emma-container"><div class="emma-icon">🐮</div><div class="emma-label">EMMA</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-reise">', unsafe_allow_html=True)
        if st.button("📚", key="r_btn"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Zeig mir dein Buch!")})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-dinge">', unsafe_allow_html=True)
        if st.button("🌍", key="d_btn"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Was willst du mir zeigen?")})
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
        if st.button("🔙", key="b_btn"):
            st.session_state.update({"seite": "start", "modus": "start"})
            for k in ['audio', 'last_img_hash']: st.session_state.pop(k, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊", key="p_btn"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # WICHTIG: Absolut saubere Einrückung hier
    bild_datei = st.camera_input("")
    st.markdown('<div class="click-here">👇</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            with st.spinner(" "): 
                st.markdown('<div class="waiting-emma">🐮</div>', unsafe_allow_html=True)
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                safety = "SICHERHEIT: Falls Gewalt/Sexualität, sag: 'Das möchte ich nicht sehen.'."
                if st.session_state['modus'] == "entdeckungsreise":
                    p = f"{safety} Du bist EMMA. Buch: Vorlesen. Klappe: Suchen. Heft: Aufgabe erklären. Max 3 Sätze."
                else:
                    p = f"{safety} Du bist EMMA. Erkläre das Foto kindgerecht. Max 2 Sätze."
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
