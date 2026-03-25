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

# --- 2. EINFACHES, STABILES DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Buttons groß und kinderfreundlich */
    .stButton > button { 
        border-radius: 20px !important; 
        border: 4px solid white !important; 
        height: 100px !important;
        width: 100% !important;
        font-size: 40px !important;
        background-color: white !important;
        margin-bottom: 10px;
    }
    
    /* Kamera-Button auffällig */
    .stCameraInput button {
        background-color: #A5D6A7 !important;
        color: white !important;
    }

    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .finger { text-align: center; font-size: 50px; animation: bounce 1s infinite; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

# Session State Initialisierung
if 'seite' not in st.session_state: st.session_state['seite'] = 'start'
if 'modus' not in st.session_state: st.session_state['modus'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;">EMMA</h1>', unsafe_allow_html=True)
    
    # Wir nutzen hier die einfache Untereinander-Anordnung, die sicher funktioniert
    if st.button("📚 Bilderbuch entdecken", key="start_reise"):
        st.session_state['modus'] = "entdeckungsreise"
        st.session_state['seite'] = "kamera"
        st.session_state['welcome_audio'] = get_emma_audio("Hallo! Zeig mir dein Buch!")
        st.rerun()
        
    if st.button("🌍 Dinge erkunden", key="start_dinge"):
        st.session_state['modus'] = "dinge"
        st.session_state['seite'] = "kamera"
        st.session_state['welcome_audio'] = get_emma_audio("Hallo! Was willst du mir zeigen?")
        st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    # Willkommens-Audio
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    # Obere Navigations-Buttons
    if st.button("🔙 Zurück zum Start", key="nav_back"):
        for k in ['audio', 'last_img_hash', 'processing']: 
            if k in st.session_state: del st.session_state[k]
        st.session_state['seite'] = 'start'
        st.rerun()

    # Lautsprecher-Button (verschwindet bei neuem Foto)
    if 'audio' in st.session_state and not st.session_state.get('processing', False):
        if st.button("🔊 Noch mal hören", key="play_audio"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Kamera-Input (Standard-Funktion ohne CSS-Eingriff)
    bild_datei = st.camera_input("Foto")
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Neue Foto-Logik
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['processing'] = True
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            
            with st.spinner("Emma schaut ganz genau hin..."):
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # Modus-spezifische Anweisungen
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = "Du bist EMMA. Lies zuerst den Text im Bild komplett vor. Wenn du Klappen oder Laschen im Buch entdeckst, frage das Kind danach. Max 3 Sätze."
                else:
                    prompt = "Du bist EMMA. Erkläre dieses Bild für ein 5-jähriges Kind in maximal 2 Sätzen."
                
                try:
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}]
                    )
                    
                    st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                    st.session_state['processing'] = False
                    st.rerun()
                except Exception as e:
                    st.error("Da ist etwas schief gelaufen. Bitte versuch es noch mal!")
                    st.session_state['processing'] = False
