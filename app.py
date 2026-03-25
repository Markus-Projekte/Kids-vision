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

# --- 2. DESIGN (MIT KLAPPEN-HINWEIS & BUTTON-TRICK) ---
if st.session_state.get('modus') == "entdeckungsreise":
    bg_color = "#E3F2FD"
    secondary_bg = "#BBDEFB"
else:
    bg_color = "#FFF9C4"
    secondary_bg = "#FFFDE7"

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 100%); }}
    
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
    @keyframes wiggle {{ 0%, 100% {{ transform: rotate(-5deg); }} 50% {{ transform: rotate(5deg); }} }}
    
    .waiting-emma {{ font-size: 80px; animation: bounce 1s infinite ease-in-out; text-align: center; margin: 20px; }}
    
    .emma-container {{ text-align: center; padding: 10px; }}
    .emma-icon {{ font-size: 70px; animation: bounce 2s infinite ease-in-out; }}
    .emma-label {{ font-size: 30px; font-family: 'Arial Black', sans-serif; color: #5D4037; }}
    
    /* Kamera-Button optisch hervorheben */
    .stCameraInput button {{
        background-color: #FF5252 !important;
        color: white !important;
        border: 4px solid white !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2) !important;
    }}
    
    /* Kleiner Zeigepfeil für den Kamera-Knopf */
    .click-here {{
        text-align: center;
        font-size: 40px;
        animation: bounce 1s infinite;
        margin-bottom: -10px;
    }}

    [data-testid="stHorizontalBlock"] {{ display: flex !important; justify-content: center !important; gap: 20px !important; }}
    .stButton > button {{ border-radius: 35px !important; border: 5px solid white !important; height: 125px !important; width: 125px !important; }}
    .stButton p {{ font-size: 60px !important; }}
    .btn-reise button {{ background-color: #00B0FF !important; }} 
    .btn-dinge button {{ background-color: #4CAF50 !important; }} 
    .back-btn button {{ background-color: #FF7043 !important; height: 65px !important; width: 65px !important; }}
    .play-btn button {{ background-color: #FDD835 !important; height: 80px !important; width: 80px !important; }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emma-container"><div class="emma-icon">🐮</div><div class="emma-label">EMMA</div></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-reise">', unsafe_allow_html=True)
        if st.button("📚"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Ich bin EMMA. Zeig mir dein Buch oder dein Heft!")})
            st.rerun()
    with col2:
        st.markdown('<div class="btn-dinge">', unsafe_allow_html=True)
        if st.button("🌍"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Schau mal, ich bin EMMA! Magst du mir ein Foto machen?")})
            st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("🔙"):
            st.session_state.update({"seite": "start", "modus": "start"})
            for k in ['audio', 'last_img_hash']: st.session_state.pop(k, None)
            st.rerun()
    with c2: st.markdown('<div style="font-size: 50px; text-align: center;">🐮</div>', unsafe_allow_html=True)
    with c3:
        if 'audio' in st.session_state:
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Visueller Hinweis über der Kamera
    st.markdown('<div class="click-here">👇</div>', unsafe_allow_html=True)
    bild_datei = st.camera_input("")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            with st.spinner(" "): 
                st.markdown('<div class="waiting-emma">🐮</div>', unsafe_allow_html=True)
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # --- PROMPT MIT KLAPPEN-LOGIK ---
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = """Du bist EMMA, eine herzliche Kuh. 
                    1. Wenn es ein BUCH ist: Lies den Text vor.
                    2. ACHTUNG KLAPPEN: Suche nach Hinweisen auf Klappen (Laschen, Kerben). Wenn du eine siehst, sag am Ende: 'Oh, da ist ja eine Klappe! Magst du sie mal für mich aufmachen und mir zeigen?'
                    3. Wenn es ein HEFT ist: Erkläre die Aufgabe ganz einfach.
                    Sprich sanft und max. 3 Sätze."""
                else:
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
