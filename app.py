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

# --- 2. STYLING (Flachere & Breitere Buttons) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Haupt-Buttons: Flacher, breiter, moderner */
    .stButton > button { 
        border-radius: 15px !important; 
        border: 3px solid white !important; 
        height: 80px !important; /* Etwas flacher */
        width: 100% !important;   /* Volle Breite */
        font-size: 24px !important;
        font-weight: bold !important;
        background-color: white !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1) !important;
        margin-bottom: 15px;
    }
    
    /* Emojis in den Buttons größer machen */
    .stButton p { font-size: 35px !important; }

    .stCameraInput button {
        background-color: #A5D6A7 !important;
        color: white !important;
        height: 50px !important;
    }

    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .finger { text-align: center; font-size: 50px; animation: bounce 1s infinite; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037;">EMMA</h1>', unsafe_allow_html=True)
    
    st.write("### Was machen wir heute?")
    
    if st.button("📚 BÜCHER LESEN", key="start_r"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
        
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Was hast du da?")})
        st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    # Breiter ZURÜCK Button
    if st.button("🔙 ZURÜCK", key="nav_b"):
        for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
            if k in st.session_state: st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    
    # Lautsprecher Button
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        if st.button("🔊 NOCHMAL HÖREN", key="play_a"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("📸")
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['show_audio'] = False
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # --- DER INTELLIGENTE PROMPT ---
            if st.session_state['modus'] == "entdeckungsreise":
                prompt = """Du bist EMMA. 
                1. Check: Wenn Bild zu dunkel/unscharf -> sag es lieb.
                2. LIES DEN TEXT im Bild präzise vor.
                3. NUR WENN du auf dem Bild wirklich Klappen, Laschen oder Papierkanten siehst, die man öffnen kann: Frage danach. Wenn das Buch keine Klappen hat, erwähne sie NICHT.
                Max 4 Sätze."""
            else:
                prompt = "Du bist EMMA. Erkläre das Foto kindgerecht in 2 Sätzen."
            
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
                st.session_state['show_audio'] = True
                st.rerun()
            except:
                st.session_state['processing'] = False
                st.rerun()
