import hashlib
import base64
import openai
import streamlit as st

# --- 1. SETUP ---
st.set_page_config(page_title="Kids Vision: EMMA", page_icon="🐮")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. EINFACHES STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9C4; }
    .stButton > button { 
        border-radius: 20px; 
        height: 100px; 
        width: 100px; 
        font-size: 40px; 
    }
    .stCameraInput button { background-color: #A5D6A7 !important; }
    </style>
    """, unsafe_allow_html=True)

def get_emma_audio(text):
    # Wir nutzen hier wieder die Standardstimme, die stabil lief
    response = client.audio.speech.create(model="tts-1", voice="nova", speed=0.9, input=text)
    return base64.b64encode(response.content).decode('utf-8')

if 'seite' not in st.session_state: st.session_state['seite'] = 'start'

# --- 3. STARTSEITE ---
if st.session_state['seite'] == 'start':
    st.markdown("<h1 style='text-align:center;'>🐮 EMMA</h1>", unsafe_allow_html=True)
    
    # Wir nutzen einfache Buttons untereinander für maximale Stabilität
    if st.button("📚 Entdecker"):
        st.session_state.update({"modus": "entdeckungsreise", "seite": "kamera", "audio_welcome": get_emma_audio("Hallo! Zeig mir dein Buch!")})
        st.rerun()
        
    if st.button("🌍 Welt"):
        st.session_state.update({"modus": "dinge", "seite": "kamera", "audio_welcome": get_emma_audio("Hallo! Was ist das?")})
        st.rerun()

# --- 4. KAMERA-SEITE ---
elif st.session_state['seite'] == 'kamera':
    if 'audio_welcome' in st.session_state:
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio_welcome"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        del st.session_state['audio_welcome']

    if st.button("🔙 Zurück"):
        for k in ['audio', 'last_img_hash']: st.session_state.pop(k, None)
        st.session_state['seite'] = 'start'
        st.rerun()

    if 'audio' in st.session_state:
        if st.button("🔊 Hören"):
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{st.session_state["audio"]}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    bild_datei = st.camera_input("Foto machen")
    st.write("👆 Bitte hier drücken!")

    if bild_datei:
        img_bytes = bild_datei.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Nur wenn das Bild wirklich neu ist:
        if st.session_state.get('last_img_hash') != img_hash:
            st.session_state['last_img_hash'] = img_hash
            # Altes Audio sofort löschen, damit es nicht nochmal spielt
            if 'audio' in st.session_state: del st.session_state['audio']
            
            with st.spinner("Emma schaut hin..."):
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                prompt = "Du bist EMMA. Erkläre das Bild für ein Kind in max 3 Sätzen."
                if st.session_state['modus'] == "entdeckungsreise":
                    prompt = "Du bist EMMA. Lies den Text im Buch vor und frage nach Klappen. Max 3 Sätze."
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                )
                st.session_state['audio'] = get_emma_audio(res.choices[0].message.content)
                st.rerun()
