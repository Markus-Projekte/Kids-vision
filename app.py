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

# --- 2. STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    .stButton > button { 
        border-radius: 15px !important; 
        border: 3px solid white !important; 
        height: 70px !important; 
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1) !important;
        margin-bottom: 10px;
        color: #5D4037 !important;
    }

    /* Farben */
    .btn-buch button { background-color: #BBDEFB !important; } /* Blau */
    .btn-welt button { background-color: #C8E6C9 !important; } /* Grün */
    .btn-back button { background-color: #FFCCBC !important; } /* Koralle */
    .btn-play button { background-color: #FFF59D !important; } /* Gelb */

    /* Emojis */
    .stButton p { font-size: 26px !important; margin: 0; }

    /* Kamera-Anpassung & FOTO MACHEN Button */
    .stCameraInput label { display: none !important; } /* Versteckt das 'Kamera' Label */
    .stCameraInput button {
        background-color: #A5D6A7 !important; /* Grün */
        color: white !important;
        border: 2px solid white !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    
    /* Animation */
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
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037; margin-bottom:30px;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER LESEN", key="start_r"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Was hast du da?")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    # Zurück-Button
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("ZURÜCK ZUM START", key="nav_back_de"):
        for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
            st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lautsprecher Button (Geänderter Text!)
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
        if st.button("🔊 ANHÖREN", key="play_audio_de"): # Umbenannt!
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Kamera mit deutschem Button! (Label versteckt durch CSS)
    bild_datei = st.camera_input("Foto") 
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['show_audio'] = False
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            if st.session_state['modus'] == "entdeckungsreise":
                prompt = """Du bist EMMA. 
                1. LIES DEN TEXT im Bild präzise vor.
                2. Wenn du Aufgaben siehst, erkläre sie kurz.
                3. NUR WENN du SICHER bist, dass Klappen oder Laschen da sind, frage danach. 
                WICHTIG: Wenn du KEINE Klappen siehst, verliere KEIN WORT darüber.
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
