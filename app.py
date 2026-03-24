import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision", page_icon="👀", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. KINDGERECHTES DESIGN ---
st.markdown("""
    <style>
    /* Hintergrund mit sanftem Verlauf */
    .stApp {
        background: linear-gradient(180deg, #e3f2fd 0%, #f1f8e9 100%);
    }
    
    .kids-title {
        font-size: 55px;
        color: #2e7d32;
        text-align: center;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-shadow: 2px 2px white;
        margin-bottom: 10px;
    }

    /* Startkarten für die Modi */
    .mode-card {
        background: white;
        border-radius: 40px;
        padding: 20px;
        text-align: center;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
        border: 4px solid #81c784;
        margin: 10px;
    }

    /* Riesige Buttons */
    div.stButton > button {
        border-radius: 35px;
        height: 180px;
        width: 100%;
        font-size: 80px !important;
        transition: transform 0.2s;
        border: none;
    }
    
    div.stButton > button:hover {
        transform: scale(1.05);
    }

    /* Spezifische Farben für die Buttons */
    .btn-lernen div button { background-color: #42a5f5 !important; border-bottom: 8px solid #1e88e5 !important; }
    .btn-entdecken div button { background-color: #66bb6a !important; border-bottom: 8px solid #43a047 !important; }
    
    /* Der grüne Play-Button */
    .play-btn div button {
        background-color: #ffca28 !important;
        border-bottom: 8px solid #ffb300 !important;
        height: 140px;
        font-size: 70px !important;
    }

    /* Zurück-Button */
    .back-btn div button {
        height: 50px;
        font-size: 20px !important;
        background-color: #ef5350 !important;
        color: white !important;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation initialisieren
if 'seite' not in st.session_state:
    st.session_state['seite'] = 'start'

# --- 3. SEITE 1: STARTSEITE (DIE SPIELWELT) ---
if st.session_state['seite'] == 'start':
    st.markdown('<div class="kids-title">👀 Kids Vision</div>', unsafe_allow_html=True)
    
    # Zwei große Bereiche
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="mode-card" style="border-color: #42a5f5;">', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 20px; font-weight: bold; color: #1e88e5;'>Bücher & Lernen</p>", unsafe_allow_html=True)
        st.markdown('<div class="btn-lernen">', unsafe_allow_html=True)
        if st.button("📚"):
            st.session_state['modus'] = "lernen"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="mode-card" style="border-color: #66bb6a;">', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 20px; font-weight: bold; color: #2e7d32;'>Welt entdecken</p>", unsafe_allow_html=True)
        st.markdown('<div class="btn-entdecken">', unsafe_allow_html=True)
        if st.button("🌍"):
            st.session_state['modus'] = "entdecken"
            st.session_state['seite'] = 'kamera'
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# --- 4. SEITE 2: KAMERA-MODUS ---
elif st.session_state['seite'] == 'kamera':
    # Kleiner Header mit Zurück-Option
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️"):
            st.session_state['seite'] = 'start'
            if 'audio' in st.session_state: del st.session_state['audio']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    icon = "📖" if st.session_state['modus'] == "lernen" else "🔍"
    st.markdown(f"<h1 style='text-align: center; margin-top: -20px;'>{icon}</h1>", unsafe_allow_html=True)

    bild_datei = st.camera_input(" ")

    if bild_datei:
        aktuelles_bild = bild_datei.getvalue()
        
        # Reset bei neuem Bild
        if 'last_img' not in st.session_state or st.session_state['last_img'] != aktuelles_bild:
            st.session_state['last_img'] = aktuelles_bild
            if 'audio' in st.session_state: del st.session_state['audio']

        if 'audio' not in st.session_state:
            with st.spinner("🧙‍♂️ Zauberei..."):
                if st.session_state['modus'] == "lernen":
                    prompt = "Lies den Text vor oder erkläre die Aufgabe. Max 3 Sätze. Sei wie ein lieber Lehrer."
                else:
                    prompt = "Erkläre kurz was das ist und sag eine lustige Sache dazu. Max 2 Sätze. Sei wie ein Entdecker-Freund."
                
                base64_image = base64.b64encode(aktuelles_bild).decode('utf-8')
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                audio_res = client.audio.speech.create(model="tts-1", voice="shimmer", input=res.choices[0].message.content)
                st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')

        if 'audio' in st.session_state:
            st.markdown('<div class="play-btn">', unsafe_allow_html=True)
            if st.button("🔊"):
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                st.balloons()
            st.markdown('</div>', unsafe_allow_html=True)
