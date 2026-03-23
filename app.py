import streamlit as st
import openai
import base64

# --- SICHERHEITS-CHECK ---
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("🔑 API-Key fehlt! Bitte in den Streamlit-Secrets hinterlegen.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

st.title("✨ Dein Zauber-Stift")

bild_datei = st.camera_input("Foto machen zum Vorlesen!")

if bild_datei:
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    with st.spinner("Ich denke nach..."):
        try:
            # 1. BILD ANALYSIEREN
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Erkläre kurz was auf dem Bild ist für ein 4-jähriges Kind."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ],
                    }
                ],
            )
            text = response.choices[0].message.content
            st.write(text)

            # 2. SPRACHE ERZEUGEN
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer",
                input=text
            )
            
            # 3. ABSPIELEN
            st.audio(audio_response.content, format="audio/mp3", autoplay=True)

        except Exception as e:
            # Falls OpenAI nein sagt, schreiben wir hier warum:
            st.error(f"Oh weh, ein kleiner Fehler: {e}")
            st.info("Tipp: Prüfe dein Guthaben bei OpenAI unter 'Billing'.")
