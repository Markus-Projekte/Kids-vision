import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision: EMMI", page_icon="🐮", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. SCHLANKES DESIGN (Fokus auf Stabilität) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF9C4 0%, #FFFDE7 100%); }
    
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    
    .emmi-container { text-align: center; margin-top: -20px; margin-bottom: 10px; }
    .emmi-icon { font-size: 80px; animation: bounce 2s infinite ease-in-out; }
    .emmi-label { font-size: 28px; font-family: 'Arial Black', sans-serif; color: #5D4037; margin-top: -5px; }

    /* Zentrierung der Start-Buttons */
    .start-grid {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }
    
    /* Button Styles */
    .stButton > button { 
        border-radius: 30px !important; 
        border: 6px solid white !important; 
        box-shadow: 0px 5px 0px rgba(0,0,0,0.05);
        height: 140px !important;
        width: 140px !important;
    }
    .stButton p { font-size: 60px !important; }
    
    /* Farben */
    .btn-lernen button { background-color: #B3E5FC !important; } 
    .btn-entdecken button { background-color: #C8E6C9 !important; } 
    .back-btn button { background-color: #FFCCBC !important; height: 60px !important; width: 60px !important; }
    .play-btn button { background-color: #FFF9C4 !important; height: 70px !important; width: 70px !important; }
    
    /* Kamera-Vorschau Fix: Sicherstellen, dass nichts drüber liegt */
    .stCameraInput { margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="emmi-container"><div class="emmi-icon">🐮</div><div class="emmi-label">EMMI</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2) # Streamlit Spalten sind für die Zentrierung am sichersten
    with col1:
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚", key="lernen"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍", key="entdecken"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SEITE 2: KAMERA ---
elif st.session_state['seite'] == 'kamera':
    col_back, col_emy, col_play = st.columns([1,1,1])
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_emy:
        st.markdown('<div style="font-size: 50px; text-align: center;">🐮</div>', unsafe_allow_html=True)

    with col_play:
        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Einfacher Kamera-Input für maximale Stabilität
    bild_datei = st.camera_input("Schau mal!")

    if bild_datei:
        # Nur verarbeiten, wenn es ein neues Bild ist
        if 'last_img_id' not in st.session_state or st.session_state['last_img_id'] != bild_datei.id:
            st.session_state['last_img_id'] = bild_datei.id
            
            with st.spinner("EMMI schaut hin..."):
                base64_image = base64.b64encode(bild_datei.getvalue()).decode('utf-8')
                
                prompt = "Du bist Kuh EMMI. Erkläre kurz (max 3 Sätze) was du siehst und nenne einen spannenden Fakt für ein Kind."
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                
                audio_res = client.audio.speech.create(model="tts-1", voice="alloy", input=res.choices[0].message.content)
                st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')
                st.rerun()
