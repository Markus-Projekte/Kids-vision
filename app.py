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

# --- 2. STYLING (Inklusive LED-Logik) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    /* Haupt-Buttons */
    .stButton > button { 
        border-radius: 20px !important; 
        border: 3px solid white !important; 
        height: 70px !important; 
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        color: #5D4037 !important;
    }

    .btn-buch button { background-color: #BBDEFB !important; }
    .btn-welt button { background-color: #C8E6C9 !important; }
    .btn-back button { background-color: #FFCCBC !important; }
    
    /* Der "ANHÖREN" Button wird zur grünen LED */
    .btn-led-gruen button { 
        background-color: #4CAF50 !important; 
        color: white !important;
        border: 5px solid #E8F5E9 !important;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(76, 175, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }

    .status-rot {
        background-color: #FF5252;
        color: white;
        padding: 10px;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: inline-block;
        margin-bottom: 10px;
        border: 3px solid white;
    }
    
    .stCameraInput { border: 8px solid #5D4037 !important; border-radius: 25px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER ENTDECKEN"):
        st.session_state.update({"modus": "buch", "seite": "kamera"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN"):
        st.session_state.update({"modus": "welt", "seite": "kamera"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("🔙 ZURÜCK"):
        for k in ['audio', 'last_img_hash', 'processing']: 
            st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # LED LOGIK ANZEIGE
    if st.session_state.get('processing'):
        st.markdown('<div style="text-align:center;"><div class="status-rot"></div><br><b>Emma denkt nach...</b></div>', unsafe_allow_html=True)
    
    if 'audio' in st.session_state and not st.session_state.get('processing'):
        st.markdown('<div class="btn-led-gruen">', unsafe_allow_html=True)
        if st.button("🔊 JETZT ANHÖREN"):
            # Das Audio wird erst beim Klick in die Seite geladen
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto machen") 

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state.update({'last_img_hash': img_hash, 'processing': True})
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
        
        # Einfacher, stabiler Prompt
        prompt = "Du bist EMMA. Erkläre das Bild kindgerecht in 3 Sätzen."
        if st.session_state['modus'] == "buch":
            prompt = "Du bist EMMA. Lies den Text im Bild vor. Max 4 Sätze."
        
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
            )
            # Audio generieren und speichern
            st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
            st.session_state['processing'] = False
            st.rerun()
        except:
            st.session_state['processing'] = False
            st.error("Fehler bei der Verbindung.")
