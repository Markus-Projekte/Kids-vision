import streamlit as st
import base64
import requests

# --- KONFIGURATION ---
# Stelle sicher, dass dein OpenAI Key in den Streamlit Secrets hinterlegt ist
api_key = st.secrets["OPENAI_API_KEY"]

def get_baeren_audio(text):
    """Erzeugt die brummige Bärenstimme via OpenAI TTS"""
    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "tts-1",
            "voice": "onyx", 
            "input": text
        }
    )
    return response.content

def ask_baer(image_base64):
    """Die Story-Engine für lange Geschichten"""
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Du bist der weise Erzählbär von KIDS VISION. Erzähle eine gemütliche, spannende Enkelgeschichte (ca. 800-1000 Wörter). Nutze Bären-Ausdrücke wie 'Huiuiui' oder 'In meinen alten Tatzen'. Sei gütig und fantasievoll."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Was siehst du auf diesem Foto? Erzähl mir eine Legende dazu!"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ],
        "max_tokens": 2500
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}"}, json=payload)
    return response.json()['choices'][0]['message']['content']

# --- STREAMLIT UI ---
st.set_page_config(page_title="KIDS VISION - Der Erzählbär", page_icon="🐻")

# Das Logo laden (muss im selben GitHub-Ordner liegen)
try:
    st.image("baer_logo.png", width=400)
except:
    st.info("🐻 Der Erzählbär macht sich gerade bereit...")

st.title("Der Erzählbär")
st.write("Huiuiui! Zeig mir ein Bild, und ich erzähle dir eine Geschichte aus meiner alten Schatztruhe...")

img_file = st.camera_input("Foto machen")

if img_file:
    with st.spinner("Lass mich mal kurz nachdenken..."):
        bytes_data = img_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        
        # Geschichte und Audio generieren
        story_text = ask_baer(base64_image)
        audio_data = get_baeren_audio(story_text)
        
        # Anzeige
        st.subheader("Die Geschichte des Erzählbären:")
        st.write(story_text)
        st.audio(audio_data, format="audio/mp3")
