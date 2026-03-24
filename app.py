import streamlit as st
import openai
import base64

# --- 1. CONFIG & SICHERHEIT ---
# Wir setzen den Seitentitel und das Icon für den Browser-Tab
st.set_page_config(page_title="Kids Vision", page_icon="👀")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("🔑 API-Key fehlt! Bitte in den Streamlit-Secrets hinterlegen.")
    st.stop()

# --- 2. KINDGERECHTES DESIGN (CSS) ---
# Hier machen wir die App bunt und weich
st.markdown("""
    <style>
    /* Hintergrundfarbe der ganzen App (Hellblau) */
    .stApp {
        background-color: #E0F7FA;
    }
    
    /* Titel-Styling (Groß, Bunt, Mittig) */
    .kids-title {
        font-size: 50px;
        color: #FF6F00;
        text-align: center;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        margin-bottom: 20px;
    }
    
    /* Styling für den Kamera-Eingabe-Bereich */
    .stCameraInput > label {
        font-size: 24px;
        color: #01579B;
        font-weight: bold;
    }
    
    /* Styling für den riesigen HÖREN-Button (Grün) */
    div.stButton > button:first-child {
        background-color: #4CAF50; /* Grün */
        color: white;
        font-size: 32px;
        font-weight: bold;
        height: 120px;
        width: 100%;
        border-radius: 30px; /* Sehr runde Ecken */
        border: 5px solid #8BC34A;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
        margin-top: 20px;
    }
    
    /* Abgerundete Ecken für Bilder */
    .stImage > img {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HAUPTBEREICH & TITEL ---
st.markdown('<div class="kids-title">👀 Kids Vision</div>', unsafe_allow_html=True)

# --- 4. KAMERA-EINGABE ---
# Wir nutzen Emojis und einfachen Text, um den Standard-Text zu überdecken
# st.camera_input ist intern schwer zu stylen, aber der Label-Text hilft
bild_datei = st.camera_input("📸 1. Foto machen")

if bild_datei:
    # Bild verarbeiten
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    # Wir speichern das Ergebnis in der "Session", damit es nicht verschwindet
    if 'audio_b64' not in st.session_state:
        # Ein kinderfreundlicher Lade-Text
        with st.spinner("Moment, ich schaue es mir an... 🧙‍♂️"):
            try:
                # KI ANFRAGE (GPT-4o)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "user", "content": [
                            {
                                "type": "text", 
                                "text": "Du bist ein magischer Vorlese-Stift für ein 4-jähriges Kind. Erkläre kurz und einfach, was auf dem Bild zu sehen ist oder welche Aufgabe dort steht. Max 2 Sätze. Antworte direkt dem Kind."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]}
                    ],
                )
                text_antwort = response.choices[0].message.content
                st.session_state['text_antwort'] = text_antwort

                # STIMME ERZEUGEN
                audio_response = client.audio.speech.create(
                    model="tts-1",
                    voice="shimmer", # Eine freundliche, weibliche Stimme
                    input=text_antwort
                )
                st.session_state['audio_b64'] = base64.b64encode(audio_response.content).decode('utf-8')
            except Exception as e:
                st.error(f"Oh weh, ein kleiner Fehler: {e}")

    # --- 5. ERGEBNIS-ANZEIGE ---
    # Wenn alles bereit ist, zeigen wir den Text und den RIESIGEN Knopf
    if 'audio_b64' in st.session_state:
        # Großer Text für die Kinder (Subheader)
        st.subheader(st.session_state['text_antwort'])
        
        # Der magische Knopf für das Kind
        if st.button("🔊 2. HÖREN!"):
            # HTML für sofortiges Abspielen nach Klick
            audio_html = f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{st.session_state['audio_b64']}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            st.balloons() # Ein bisschen Spaß zur Belohnung!
