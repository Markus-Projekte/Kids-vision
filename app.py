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
st.title("✨ Dein Zauber-Stift")

# WICHTIG: Kurze Anleitung für das Kind (kann man später als Icon machen)
st.write("Mach ein Foto und ich erzähle dir, was ich sehe!")

bild_datei = st.camera_input("Tippe hier für das Foto!")

if bild_datei:
    # Bild verarbeiten
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    with st.spinner("Ich schaue es mir an... 🧙‍♂️"):
        try:
            # 1. KI ANFRAGE (GPT-4o)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Erkläre kurz für ein 4-jähriges Kind, was auf dem Bild ist. Max 2 Sätze. Antworte direkt dem Kind."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ],
                    }
                ],
            )
            text_antwort = response.choices[0].message.content
            st.subheader(text_antwort) # Großer Text für die Kinder

            # 2. STIMME ERZEUGEN
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer",
                input=text_antwort
            )
            
            # 3. DER ULTIMATIVE AUTOPLAY-TRICK
            audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
            
            # Dieser HTML-Code erzwingt das Abspielen
            audio_html = f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Fehler: {e}")

with st.expander("Info für Eltern"):
    st.write("Hinweis: Falls kein Ton kommt, prüfen Sie, ob das Handy auf 'Lautlos' steht oder die Medienlautstärke leise ist.")
