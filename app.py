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
        border-radius: 20px !important; 
        border: 4px solid white !important; 
        height: 100px !important;
        width: 100% !important;
        font-size: 45px !important;
        background-color: white !important;
    }
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

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;">EMMA</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚", key="start_r"):
            st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Zeig mir dein Buch!")})
            st.rerun()
    with col2:
        if st.button("🌍", key="start_w"):
            st.session_state.update({"modus": "dinge", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Was hast du da?")})
            st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙", key="nav_b"):
            for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
                if k in st.session_state: st.session_state.pop(k, None)
            st.session_state['seite'] = 'start'
            st.rerun()
    
    with col2:
        if st.session_state.get('show_audio') and 'audio' in st.session_state:
            if st.button("🔊", key="play_a"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("📸")
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    # Bild-Erkennung
    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['show_audio'] = False
            if 'audio' in st.session_state: del st.session_state['audio']
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun()

    # EMMA arbeitet
    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # Schärfere Anweisungen & Licht-Check
            if st.session_state['modus'] == "entdeckungsreise":
                prompt = """Du bist EMMA, die schlaue Kuh. 
                1. Check: Ist das Bild zu dunkel, extrem unscharf oder gar kein Buch zu sehen? Dann sag: 'Oh, es ist ein bisschen dunkel. Kannst du das Licht anmachen und noch ein Foto machen?'
                2. Wenn alles okay ist: LIES DEN TEXT VOR, den du im Buch siehst. Sei präzise.
                3. Suche nach Klappen/Laschen und frage danach. Max 4 Sätze."""
            else:
                prompt = "Du bist EMMA. Erkläre das Foto kindgerecht. Wenn es zu dunkel ist, sag Bescheid. Max 2 Sätze."
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                antwort = res.choices[0].message.content
                st.session_state['audio'] = get_emma_audio(antwort)
                st.session_state['processing'] = False
                st.session_state['show_audio'] = True
                st.rerun()
            except:
                st.session_state['processing'] = False
                st.rerun()
