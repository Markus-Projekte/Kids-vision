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

# --- 2. DYNAMISCHES DESIGN (KOMPAKT & NEBENEINANDER) ---
if st.session_state.get('modus') == "entdeckungsreise":
    bg_color = "#E3F2FD"
    secondary_bg = "#BBDEFB"
else:
    bg_color = "#FFF9C4"
    secondary_bg = "#FFFDE7"

st.markdown(f"""
    <style>
    /* Hintergrund */
    .stApp {{ background: linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 100%); }}
    
    /* Animationen */
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
    .waiting-emma {{ font-size: 80px; animation: bounce 1s infinite ease-in-out; text-align: center; margin: 20px; }}
    
    /* EMMA-Kopf */
    .emma-container {{ text-align: center; padding: 10px; margin-bottom: -15px; }}
    .emma-icon {{ font-size: 70px; animation: bounce 2s infinite ease-in-out; }}
    .emma-label {{ font-size: 30px; font-family: 'Arial Black', sans-serif; color: #5D4037; }}
    
    /* Buttons zentrieren und nebeneinander */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 15px !important;
        width: 100% !important;
        margin-top: -10px !important;
    }}

    /* Generelle Button-Größe & Abrundung */
    .stButton > button {{ 
        border-radius: 35px !important; 
        border: 5px solid white !important; 
        box-shadow: 0px 6px 12px rgba(0,0,0,0.1);
        height: 125px !important; /* Etwas kompakter */
        width: 125px !important;  /* Etwas kompakter */
    }}
    .stButton p {{ font-size: 60px !important; }}
    
    /* Modus-Farben */
    .btn-reise button {{ background-color: #00B0FF !important; }} 
    .btn-dinge button {{ background-color: #4CAF50 !important; }} 
    .back-btn button {{ background-color: #FF7043 !important; height: 65px !important; width: 65px !important; }}
    .play-btn button {{ background-color: #FDD835 !important; height: 65px !important; width: 65px !important; }}
    
    /* Kamera-Layout: Kompakt und keine Kuh oben */
    .stCameraInput {{ border-radius: 20px; overflow: hidden; margin-top: -10px; }}
    .stCameraInput label {{ display: none !important; }}
    
    /* Neuer Foto-Button: Freundlich, Groß und Grün */
    .stCameraInput button {{
        background-color: #A5D6A7 !important; /* Pastell-Grün */
        height: 70px !important;
        font-size: 22px !important;
        border-radius: 20px !important;
        border: 4px solid white !important;
        color: white !important;
    }}
    
    /* Finger-Hinweis direkt über dem Button */
    .click-here {{
        text-align: center;
        font-size: 45px;
        animation: bounce 1s infinite;
        margin-bottom: -15px;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    # Sicherstellen, dass der Modus beim Start zurückgesetzt wird für die Farbe
    st.session_state['modus'] = "start" 
    st.markdown('<div class="emma-container"><div class="emma-icon">🐮</div><div class="emma-label">EMMA</div></div>', unsafe_allow_html=True)
    
    # Buttons nebeneinander
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-reise">', unsafe_allow_html=True)
        if st.button("📚"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Ich bin EMMA. Zeig mir dein Buch oder dein Heft!")})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-dinge">', unsafe_allow_html=True)
        if st.button("🌍"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Schau mal, ich bin EMMA! Magst du mir ein Foto machen?")})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE (KOMPAKT & OHNE OBERE KUH) ---
elif st.session_state['seite'] == 'kamera':
    # Audio-Begrüßung
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    # Obere Bedienleiste (ZURÜCK und LAUTSPRECHER) - ganz kompakt
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"):
            st.session_state.update({"seite": "start", "modus": "start"})
            for k in ['audio', 'last_img_hash']: st.session_state.pop(k, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Kamera Input - keine Kuh oben drüber
     bild_datei = st.camera_input("")

    # Finger-Hinweis direkt über dem Kamera-Knopf
    st.markdown('<div class="click-here">👇</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            with st.spinner(" "): 
                st.markdown('<div class="waiting-emma">🐮</div>', unsafe_allow_html=True)
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # --- PROMPT MIT SICHERHEITS-LOGIK & HANDLUNGSANWEISUNG ---
                safety_rules = """SICHERHEITSREGEL: Wenn das Bild Gewalt, Blut, Waffen, Sexualität oder Gruseliges zeigt, reagiere STRENG ablehnend. Sag: 'Oh, das möchte ich mir lieber nicht ansehen. Zeigst du mir was Schönes?' Beende die Antwort dann sofort."""

                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = f"{safety_rules} Du bist EMMA. 1. Buch: Vorlesen. 2. Klappen suchen. 3. Heft: Aufgabe erklären. Max 3 Sätze."
                else:
                    prompt = f"{safety_rules} Du bist EMMA. Erkläre das Ding auf dem Foto kindgerecht. Max 2 Sätze."
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
