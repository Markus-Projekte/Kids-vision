import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP & KONFIGURATION ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="🐮", layout="centered")

# API-Key Check (Wichtig für Streamlit Cloud)
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Flachere, breitere, farbige Buttons & Deutsche Kamera) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Haupt-Buttons: Flacher, breiter, moderner */
    .stButton > button { 
        border-radius: 15px !important; 
        border: 3px solid white !important; 
        height: 70px !important; /* Etwas flacher */
        width: 100% !important;   /* Volle Breite */
        font-size: 20px !important;
        font-weight: bold !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1) !important;
        margin-bottom: 15px;
        color: #5D4037 !important;
    }
    
    /* Emojis in den Buttons */
    .stButton p { font-size: 28px !important; margin: 0; }

    /* Spezifische Farben für die Buttons */
    .btn-buch button { background-color: #BBDEFB !important; } /* Blau */
    .btn-welt button { background-color: #C8E6C9 !important; } /* Grün */
    .btn-back button { background-color: #FFCCBC !important; } /* Koralle/Orange */
    .btn-play button { background-color: #FFF59D !important; } /* Gelb */

    /* Kamera-Anpassung & Deutsche Buttons */
    .stCameraInput { border-radius: 15px; overflow: hidden; }
    .stCameraInput label { display: none !important; } /* Versteckt das 'Foto' Label */
    
    /* Take Photo -> FOTO MACHEN */
    .stCameraInput button {
        background-color: #A5D6A7 !important;
        color: white !important;
        border: 2px solid white !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    
    /* Clear Photo -> Bild löschen */
    [data-testid="stCameraInputClear"] {
        background-color: #FF7043 !important; /* Rötlicher für Löschen */
        color: white !important;
        border-radius: 10px !important;
    }

    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .finger { text-align: center; font-size: 50px; animation: bounce 1s infinite; }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktion für Audio
def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

# Session State Initialisierung
if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    # Modus beim Start zurücksetzen für die Farbe
    st.session_state['modus'] = "start" 
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037; margin-bottom:30px;">EMMA</h1>', unsafe_allow_html=True)
    
    # Buttons für die beiden Abenteuer (farbig markiert)
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER LESEN", key="start_r"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Was hast du da?")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE (Flacheres Design & Deutsche Begriffe) ---
elif st.session_state['seite'] == 'kamera':
    # Audio-Begrüßung beim ersten Laden
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    # Zurück-Button (Breiter, flacher und rot eingefärbt)
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK ZUM START", key="nav_b"):
        # Alles gründlich löschen beim Zurückgehen
        for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
            if k in st.session_state: del st.session_state[k]
        st.session_state['seite'] = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lautsprecher Button (Text geändert auf ANHÖREN, nur zeigen wenn Audio da ist)
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
        if st.button("🔊 ANHÖREN", key="play_a"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Kamera Input (CSS versteckt das Standard-Label und ändert den Button auf Deutsch)
    bild_datei = st.camera_input("Foto") 
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    # Logik für neues Foto
    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Sobald ein neues Foto erkannt wird:
        if st.session_state.get('last_img_hash') != img_hash:
            # Alles alte sofort löschen, damit der Lautsprecher-Button sofort weg ist
            st.session_state['show_audio'] = False
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun() # Seite neu laden, damit der Lautsprecher-Button sofort verschwindet

    # Verarbeitung nach dem Rerun (während der Spinner dreht)
    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # --- INTELLIGENTER PROMPT MIT SCHWEIGEPFLICHT FÜR KEINE KLAPPEN ---
            if st.session_state['modus'] == "entdeckungsreise":
                prompt = """Du bist EMMA, die liebe Kuh. Deine Hauptaufgabe: LIES DEN TEXT VOR, den du auf dem Bild siehst. 
                Sei extrem genau beim Entziffern der Buchstaben. Wenn du Aufgaben siehst, erkläre sie kurz. 
                NUR WENN du auf dem Bild wirklich etwas siehst, das nach Klappen, Laschen oder Papierkanten aussieht, frage am Ende danach. 
                WICHTIG: Wenn du KEINE Klappen siehst, verliere KEIN WORT darüber. Erwähne sie niemals negativ.
                Antworte in max. 4 Sätzen."""
            else:
                prompt = "Du bist EMMA, die schlaue Kuh. Erkläre dieses Foto für ein 5-jähriges Kind in maximal 2 Sätzen."
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                
                # Audio generieren
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.session_state['processing'] = False
                st.session_state['show_audio'] = True # Erst jetzt darf der Button wieder erscheinen
                st.rerun() # Seite neu laden, um das Audio abzuspielen
            except:
                st.session_state['processing'] = False
                st.rerun()
