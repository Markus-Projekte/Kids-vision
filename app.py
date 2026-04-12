import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP (Basierend auf deiner stabilen Version) ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. STYLING (Kombination aus Stabilität & Rohr-Optik) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    
    .stButton > button { 
        border-radius: 20px !important; 
        border: 3px solid white !important; 
        height: 90px !important; 
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
        color: #5D4037 !important;
    }

    .btn-buch button { background-color: #BBDEFB !important; }
    .btn-welt button { background-color: #C8E6C9 !important; }
    .btn-back button { background-color: #FFCCBC !important; height: 60px !important; }
    .btn-play button { background-color: #FFF59D !important; border: 5px solid white !important; height: 120px !important; }

    .stCameraInput { border: 10px solid #5D4037 !important; border-radius: 30px !important; }
    .stCameraInput label { display: none !important; }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .finger { text-align: center; font-size: 50px; animation: bounce 1s infinite; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    try:
        response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
        return base64.b64encode(response.content).decode('utf-8')
    except:
        return None

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div style="text-align:center; font-size:70px; margin-top:20px;">🐮</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:#5D4037;">EMMA</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-buch">', unsafe_allow_html=True)
    if st.button("📚 BÜCHER LESEN"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="btn-welt">', unsafe_allow_html=True)
    if st.button("🌍 WELT ENTDECKEN"):
        st.session_state.update({"modus": "dinge", "seite": "kamera"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("ZURÜCK ZUM START"):
        for k in ['audio', 'last_img_hash', 'processing', 'show_audio']: 
            st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Der Anhören-Button (erscheint wie früher nach der Verarbeitung) [cite: 14]
    if st.session_state.get('show_audio') and 'audio' in st.session_state:
        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
        if st.button("🔊 ANHÖREN"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto") 
    st.markdown('<div class="finger">👆</div>', unsafe_allow_html=True)

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state.update({'show_audio': False, 'last_img_hash': img_hash, 'processing': True})
            st.rerun()

    if st.session_state.get('processing') and bild_datei:
        with st.spinner("Emma schaut..."):
            base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
            
            # Prompts aus deiner stabilen Datei [cite: 17, 20]
            if st.session_state['modus'] == "entdeckungsreise":
                prompt = "Du bist EMMA. Lies den Text im Bild präzise vor. Max 4 Sätze."
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
                
                audio_res = get_emma_audio(res.choices[0].message.content)
                if audio_res:
                    st.session_state.update({'audio': audio_res, 'processing': False, 'show_audio': True})
                    st.rerun()
            except:
                st.session_state['processing'] = False
                st.error("Verbindung kurz unterbrochen. Bitte nochmal versuchen.")
