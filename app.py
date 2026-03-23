import streamlit as st
import openai
import base64
import io

# 1. VERBINDUNG ZU OPENAI (SICHERHEIT)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("🔑 API-Key fehlt! Bitte in den Streamlit-Secrets hinterlegen.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# 2. SEITEN-DESIGN
st.set_page_config(page_title="Zauber-Stift", page_icon="🪄")
st.title("✨ Dein Zauber-Stift")
st.write("Mach ein Foto von einer Aufgabe oder etwas aus der Natur!")

# 3. KAMERA-EINGABE
bild_datei = st.camera_input("Foto machen")

if bild_datei:
    # Bild in das richtige Format umwandeln
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    with st.spinner("Ich schaue es mir an... 🧙‍♂️"):
        try:
            # A. ANFRAGE AN DAS GEHIRN (GPT-4o)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Du bist ein freundlicher Lehrer für ein 4-jähriges Kind. Erkläre kurz und einfach, was auf dem Bild zu sehen ist oder welche Aufgabe dort steht. Max. 3 Sätze."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ],
                    }
                ],
            )
            text_antwort = response.choices[0].message.content
            st.write(text_antwort)

            # B. STIMME ERZEUGEN
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer",
                input=text_antwort
            )
            
            # C. AUDIO FÜR DEN BROWSER VORBEREITEN (WICHTIG!)
            audio_data = io.BytesIO(audio_response.content)
            
            # D. ABSPIELEN
            st.audio(audio_data, format="audio/mp3")
            st.info("Tippe oben auf 'Play', um mich zu hören! 🔊")

        except Exception as e:
            st.error(f"Ein kleiner Fehler ist passiert: {e}")
            st.info("Prüfe dein Guthaben bei OpenAI (Billing).")

# --- FÜR DIE ELTERN (ZUSATZINFOS) ---
with st.expander("Info für Eltern"):
    st.write("Diese App nutzt KI, um Kindern Aufgaben vorzulesen. Bitte begleiten Sie Ihr Kind bei der Nutzung.")
