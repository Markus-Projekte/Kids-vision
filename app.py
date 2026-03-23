import streamlit as st
import openai
import base64

# 1. SICHERHEIT: Verbindung zum geheimen Schlüssel
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Stopp! Der API-Schlüssel fehlt noch in den Streamlit-Secrets.")
    st.stop()

# 2. DESIGN: Einfach und kindgerecht
st.set_page_config(page_title="Lern-Stift Kamera", page_icon="✏️")

st.title("✨ Dein Zauber-Stift")
st.write("Halte mich über ein Buch oder ein Blatt in der Natur!")

# 3. DAS AUGE: Die Kamera (Großes Fenster)
bild_datei = st.camera_input("Tippe auf den Kreis, um zu 'sehen'!")

if bild_datei:
    # Bild für die KI umwandeln
    bytes_data = bild_datei.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    with st.spinner("Ich schaue es mir an... 🧙‍♂️"):
        # 4. DAS GEHIRN: GPT-4o erkennt den Kontext automatisch
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": """
                            Du bist ein magischer Lern-Stift für ein 4-jähriges Kind. 
                            Schau dir das Bild an:
                            1. Wenn es ein Text/Rätsel ist: Lies den Text vor und erkläre kurz die Aufgabe.
                            2. Wenn es ein Natur-Objekt (Blatt, Tier, Stein) ist: Sag kurz, was es ist und eine spannende Sache dazu.
                            Antworte immer direkt an das Kind, sehr kurz (max. 3 Sätze) und in einfacher Sprache.
                            """
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ],
                }
            ],
        )

        antwort_text = response.choices[0].message.content
        
        # 5. DIE STIMME: Text in Sprache wandeln
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer", # Sanfte Stimme
            input=antwort_text
        )
        
        # Audio sofort abspielen (Autoplay)
        st.audio(audio_response.content, format="audio/mp3", autoplay=True)
        
        # Text für die Eltern zusätzlich anzeigen
        with st.expander("Für die Eltern: Was wurde gesagt?"):
            st.write(antwort_text)
