import os
os.system('pip install gtts')
import os
os.system('pip install easyocr')
import streamlit as st
import easyocr
import torch
from gtts import gTTS
from PIL import Image
import numpy as np
import base64

# =========================
# ⚙️ INITIALIZE OCR
# =========================
@st.cache_resource
def load_ocr_reader():
    # Automatically detects if GPU is available
    return easyocr.Reader(['en'], gpu=torch.cuda.is_available())

reader = load_ocr_reader()

# =========================
# 🔊 TEXT TO SPEECH (Auto-Triggered)
# =========================
def text_to_speech(text):
    if text.strip():
        try:
            tts = gTTS(text=text, lang='en')
            # Using a temporary name to avoid file-in-use errors
            audio_file = "temp_speech.mp3"
            tts.save(audio_file)
            
            with open(audio_file, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                # The 'autoplay' attribute ensures it reads immediately
                md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
                st.markdown(md, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"TTS Error: {e}")

# =========================
# 🚀 STREAMLIT UI
# =========================
st.set_page_config(page_title="SMART-APP", page_icon="📖")
st.title("SMART-APP")
st.markdown("Click the camera button below. As soon as you capture, I will read it for you.")

# 1. Camera Input (Shutter button is required by browser security)
img_file = st.camera_input("Capture Text")

if img_file:
    # Convert file to format EasyOCR understands
    image = Image.open(img_file)
    img_np = np.array(image)

    with st.spinner("🔍 Reading text..."):
        # 2. Run Pretrained EasyOCR
        results = reader.readtext(img_np, detail=0)
        full_text = " ".join(results)

    # 3. Display Results
    if full_text.strip():
        st.subheader("📝 Extracted Text:")
        st.info(full_text)
        
        # 4. 🔥 AUTO-READ (No button required)
        text_to_speech(full_text)
    else:
        st.warning("⚠️ Could not see any text. Please hold the book steady and try again.")

# Custom CSS for high readability
st.markdown("""
    <style>
    .stInfo {
        font-size: 22px;
        font-family: 'Georgia', serif;
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
