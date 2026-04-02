import streamlit as st
import easyocr
import torch
import numpy as np
from gtts import gTTS
from PIL import Image
import base64
import os

# =========================
# ⚙️ INITIALIZE OCR
# =========================
@st.cache_resource
def load_ocr():
    # Downloads pretrained weights on first run
    return easyocr.Reader(['en'], gpu=torch.cuda.is_available())

reader = load_ocr()

# =========================
# 🔊 AUTO-SPEECH ENGINE
# =========================
def speak(text):
    if text.strip():
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("speech.mp3")
            with open("speech.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                # Autoplay starts reading immediately
                md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
                st.markdown(md, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Audio Error: {e}")

# =========================
# 🚀 STREAMLIT UI
# =========================
st.set_page_config(page_title="Mobile Book Reader", page_icon="📖")
st.title("📖 Mobile Book Reader")
st.write("Capture a photo of the book page to hear it read aloud.")

# Native Mobile Camera Input
# This is much more stable than WebRTC for mobile browsers
img_file = st.camera_input("Take a photo of the page")

if img_file:
    # 1. Load Image
    image = Image.open(img_file)
    img_np = np.array(image)

    with st.spinner("🧠 Reading Book..."):
        # 2. Run EasyOCR (Pretrained ResNet Model)
        results = reader.readtext(img_np, detail=0)
        full_text = " ".join(results)

    # 3. Output Results
    if full_text.strip():
        st.subheader("📝 Text Found:")
        st.info(full_text)
        
        # 4. Auto-Read
        speak(full_text)
    else:
        st.warning("Could not find any text. Try holding the camera closer or improving the light.")

# Custom styling for mobile readability
st.markdown("""
    <style>
    .stInfo {
        font-size: 20px;
        font-family: 'serif';
        background-color: #f9f9f9;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)
