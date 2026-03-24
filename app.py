import streamlit as st
import openai
import base64

# --- API CHECK ---
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

st.set_page_config(page_title="Zauber-Stift", page_icon="🪄")

# CSS für einen riesigen, kindgerechten Button
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #FF4B4B;
        color: white;
        font-size: 30px;
        height: 150px;
        width: 100%;
        border-radius: 20px;
        border: 5px solid #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Dein Zauber-Stift")

bild_datei = st.camera_input("1. Foto machen")

if bild_datei:
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    # Wir speichern das Ergebnis in der "Session", damit es nicht verschwindet
    if 'audio_b64' not in st.session_state:
        with st.spinner("Ich schaue es mir an... 🧙‍♂️"):
            try:
                # KI ANFRAGE
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": "Erkläre kurz für ein 4-jähriges Kind, was auf dem Bild ist. Max 2 Sätze."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ],
                )
                text_antwort = response.choices[0].message.content
                st.session_state['text_antwort'] = text_antwort

                # STIMME ERZEUGEN
                audio_response = client.audio.speech.create(
                    model="tts-1",
                    voice="shimmer",
                    input=text_antwort
                )
                st.session_state['audio_b64'] = base64.b64encode(audio_response.content).decode('utf-8')
            except Exception as e:
                st.error(f"Fehler: {e}")

    # Wenn alles bereit ist, zeigen wir den Text und den RIESIGEN Knopf
    if 'audio_b64' in st.session_state:
        st.subheader(st.session_state['text_antwort'])
        
        # Der magische Knopf für das Kind
        if st.button("🔊 HÖREN!"):
            # HTML für sofortiges Abspielen nach Klick
            audio_html = f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{st.session_state['audio_b64']}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            st.balloons() # Ein bisschen Spaß für das Kind!
