import streamlit as st
import openai
import base64
import io

# 1. VERBINDUNG ZU OPENAI
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("🔑 API-Key fehlt!")
    st.stop()

client = openai.OpenAI(api_key=api_key)

st.set_page_config(page_title="Zauber-Stift", page_icon="🪄")
st.title("✨ Dein Zauber-Stift")

bild_datei = st.camera_input("Foto machen")

if bild_datei:
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    with st.spinner("Ich schaue es mir an... 🧙‍♂️"):
        try:
            # A. KI ANFRAGE
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Erkläre kurz für ein 4-jähriges Kind, was auf dem Bild ist oder was die Aufgabe ist. Max. 3 Sätze."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
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
            
            # C. DER TRICK: Audio direkt in die Seite einbetten (Base64)
            audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
            audio_tag = f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
            
            # D. ABSPIELEN ÜBER HTML (Umgeht den Standard-Player-Fehler)
            st.markdown(audio_tag, unsafe_allow_html=True)
            st.info("Hörst du mich? Falls nicht, drücke auf Play im kleinen Balken oben.")

        except Exception as e:
            st.error(f"Fehler: {e}")

with st.expander("Info für Eltern"):
    st.write("Diese App nutzt KI. Bitte begleiten Sie Ihr Kind.")
