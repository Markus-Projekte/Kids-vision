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

# --- 2. STYLING (Prototypen-Modus) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Der Button als einziger Interaktionspunkt */
    .stButton > button { 
        border-radius: 50px !important; 
        height: 80px !important; 
        font-size: 24px !important;
        font-weight: bold !important;
        background-color: #FFEB3B !important; /* Auffälliges Gelb */
        border: 4px solid white !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2) !important;
    }

    /* --- SIMULATION DES ZIELROHRS --- */
    /* Wir legen einen dunklen Rahmen um die Kamera, um das Rohr zu simulieren */
    .stCameraInput {
        border: 10px solid #5D4037 !important;
        border-radius: 20px !important;
        overflow: hidden;
    }
    
    /* Hilfstext für den Abstand */
    .status-info {
        text-align: center;
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        margin-top: 10px;
        font-weight: bold;
        color: #5D4037;
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
    st.markdown('<h1 style="text-align:center;">KIDS VISION</h1>', unsafe_allow_html=True)
    
    if st.button("📚 BÜCHER ENTDECKEN", key="start_r"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "welcome_audio": get_emma_audio("Hallo! Leg das Gerät auf dein Buch!")})
        st.rerun()

# --- 4. HARDWARE-PROTOTYP SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'welcome_audio' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["welcome_audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['welcome_audio']

    if st.button("🔙 ZURÜCK", key="nav_b"):
        st.session_state['seite'] = 'start'
        st.rerun()
    
    # Der Knopf zum Anhören (wird gelb, wenn fertig)
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        if st.button("🔊 EMMA ANHÖREN", key="play_a"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # Kamera mit visuellem Rahmen
    st.markdown('<div class="status-info">Abstand prüfen: Das Bild muss hell und scharf sein!</div>', unsafe_allow_html=True)
    bild_datei = st.camera_input("Foto") 
    
    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['show_audio'] = False
            st.session_state['last_img_hash'] = img_hash
            st.session_state['processing'] = True
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma analysiert..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # PROMPT FÜR HARDWARE-TEST (Erklärender)
            prompt = """Du bist EMMA. Erkenne Dinge oder lies Text vor. 
            Wenn das Bild zu dunkel oder unscharf ist, sag dem Kind lieb: 'Oh, es ist ein bisschen dunkel, kannst du das Licht anmachen?' 
            Ansonsten erkläre den Inhalt kindgerecht in max 3 Sätzen."""
            
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
