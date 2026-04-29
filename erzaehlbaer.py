import streamlit as st
import base64
import requests

# --- KONFIGURATION ---
api_key = st.secrets["OPENAI_API_KEY"]

def get_baeren_audio(text):
    """Wandelt Text in Sprache um. Nutzt die ersten 4000 Zeichen für Stabilität."""
    # OpenAI TTS hat ein Limit von 4096 Zeichen.
    safe_text = text[:4000] 
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "tts-1",
                "voice": "onyx", # Tiefe, gemütliche Bärenstimme
                "input": safe_text
            }
        )
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Fehler von OpenAI: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Huiuiui, meine Stimme ist weg: {e}")
        return None

def ask_baer(image_base64):
    """Generiert die Geschichte basierend auf dem Bild."""
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Du bist der weise Erzählbär von KIDS VISION. "
                    "Erzähle eine gemütliche, spannende Enkelgeschichte (ca. 600-800 Wörter). "
                    "Nutze Bären-Ausdrücke wie 'Huiuiui' oder 'In meinen alten Tatzen'. "
                    "WICHTIG: Die Geschichte muss für 3-7 Jährige geeignet sein. "
                    "Erfinde Legenden zu den Dingen, die du auf dem Foto siehst."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Was siehst du auf diesem Foto? Erzähl mir eine Geschichte!"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ],
        "max_tokens": 2000
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}"}, json=payload)
    return response.json()['choices'][0]['message']['content']

# --- STREAMLIT UI ---
st.set_page_config(page_title="KIDS VISION - Erzählbär", page_icon="🐻")

# Falls du das Bild 'baer_logo.png' in GitHub hochgeladen hast:
try:
    st.image("baer_logo.png", width=400)
except:
    st.title("🐻 Der Erzählbär")

st.write("Willkommen in meiner Kuschelecke! Zeig mir etwas, und ich erzähl dir eine Geschichte...")

img_file = st.camera_input("Foto machen")

if img_file:
    with st.spinner("Huiuiui, lass mich mal meine Brille putzen..."):
        # 1. Bild vorbereiten
        bytes_data = img_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        
        # 2. Text generieren
        story_text = ask_baer(base64_image)
        
        # 3. Audio generieren
        audio_data = get_baeren_audio(story_text)
        
        # 4. Anzeige
        st.subheader("Die Geschichte des Erzählbären:")
        st.write(story_text)
        
        if audio_data:
            st.audio(audio_data, format="audio/mp3")
        else:
            st.warning("Ich kann die Geschichte gerade nur aufschreiben, meine Stimme braucht eine Pause.")
