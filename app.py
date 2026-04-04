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

# --- 2. STYLING (Fokus auf Kamera-Wechsel-Symbol) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    .stButton > button { 
        border-radius: 20px !important; 
        border: 4px solid white !important; 
        height: 90px !important; 
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        background-color: white !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
        color: #5D4037 !important;
    }

    /* Farbakzente für die Startseite */
    .btn-buch button { background-color: #BBDEFB !important; }
    .btn-welt button { background-color: #C8E6C9 !important; }

    /* --- KAMERA-WECHSEL-SYMBOL VERSCHÖNERN --- */
    /* Wir zielen auf den Button ab, der die Kamera dreht */
    button[title="Switch camera"] {
        background-color: #FFEB3B !important; /* Auffälliges Gelb */
        border: 3px solid white !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.2) !important;
        transform: scale(1.2); /* Etwas größer machen */
    }
    
    /* Ein kleiner Text-Hinweis über der Kamera */
    .kamera-info {
        text-align: center;
        font-weight: bold;
        color: #5D4037;
        margin-bottom: 5px;
        font-size: 18px;
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
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER ENTDECKEN", key="start_r"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN", key="start_w"):
        st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_played": False, "audio_welcome": get_emma_audio("Hallo! Was willst du mir zeigen?")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state and not st.session_state.get('welcome_played', False):
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.session_state['welcome_played'] = True

    if st.button("🔙 ZURÜCK", key="nav_b"):
        for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
            st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        if st.button("🔊 ANHÖREN", key="play_a"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Info für das Kind
    st.markdown('<div class="kamera-info">Kamera drehen? Klick auf den gelben Kreis! 🔄</div>', unsafe_allow_html=True)
    
    bild_datei = st.camera_input("Foto") 
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
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.session_state['processing'] = False
                st.session_state['show_audio'] = True
                st.rerun()
            except:
                st.session_state['processing'] = False
                st.rerun()
