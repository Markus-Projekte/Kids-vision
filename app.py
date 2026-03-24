import streamlit as st
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision", page_icon="👀")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt in den Secrets!")
    st.stop()

# --- 2. DESIGN (NUR SYMBOLE & FARBEN) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; } /* Warmes Sonnengelb */
    
    /* Titel-Design */
    .kids-title { 
        font-size: 60px; 
        text-align: center; 
        margin-bottom: 30px;
    }

    /* Große Modus-Buttons */
    div.stButton > button {
        border-radius: 30px;
        height: 120px;
        font-size: 50px !important;
        border: 4px solid #FBC02D;
        box-shadow: 0px 6px 0px #F9A825;
    }
    
    /* Der Hören-Button (Aktionsfarbe) */
    .play-btn > div > button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 4px solid #388E3C !important;
        box-shadow: 0px 6px 0px #2E7D32 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="kids-title">👀 Kids Vision</div>', unsafe_allow_html=True)

# --- 3. MODUS-WAHL (Bücher oder Welt) ---
col1, col2 = st.columns(2)

with col1:
    if st.button("📚"):
        st.session_state['modus'] = "lernen"
with col2:
    if st.button("🌍"):
        st.session_state['modus'] = "entdecken"

modus = st.session_state.get('modus', 'entdecken')

# Visuelle Rückmeldung, welcher Modus aktiv ist (nur durch Icons)
if modus == "lernen":
    st.markdown("<h2 style='text-align: center;'>📖</h2>", unsafe_allow_html=True)
else:
    st.markdown("<h2 style='text-align: center;'>🔍</h2>", unsafe_allow_html=True)

# --- 4. KAMERA ---
bild_datei = st.camera_input(" ") # Kein Text-Label

if bild_datei:
    aktuelles_bild = bild_datei.getvalue()
    
    # Reset bei neuem Bild
    if 'last_img' not in st.session_state or st.session_state['last_img'] != aktuelles_bild:
        st.session_state['last_img'] = aktuelles_bild
        if 'audio' in st.session_state: del st.session_state['audio']

    if 'audio' not in st.session_state:
        with st.spinner("..."): # Minimalistisches Laden
            if modus == "lernen":
                anweisung = "Lies den Text auf dem Bild vor und erkläre kurz die Aufgabe für ein Kind (4 Jahre). Max 3 Sätze."
            else:
                anweisung = "Erkläre kurz, was das ist und sag eine spannende Sache dazu. Max 2 Sätze."

            base64_image = base64.b64encode(aktuelles_bild).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": anweisung},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}]
            )
            
            antwort = response.choices[0].message.content
            audio_res = client.audio.speech.create(model="tts-1", voice="shimmer", input=antwort)
            st.session_state['audio'] = base64.b64encode(audio_res.content).decode('utf-8')

    # --- 5. AUDIO-AUSGABE (RIESIGER BUTTON) ---
    if 'audio' in st.session_state:
        st.markdown('<div class="play-btn">', unsafe_allow_html=True)
        if st.button("🔊"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)
