import os
# Force installation of heavy libraries on first run
os.system('pip install gtts easyocr streamlit-webrtc av')

import streamlit as st
import easyocr
import torch
import av
import numpy as np
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import base64

# =========================
# ⚙️ INITIALIZE OCR
# =========================
@st.cache_resource
def load_ocr():
    # English only for speed; uses GPU if your server has one
    return easyocr.Reader(['en'], gpu=torch.cuda.is_available())

reader = load_ocr()

# =========================
# 🔊 AUTO-SPEECH ENGINE
# =========================
def speak(text):
    if text.strip():
        tts = gTTS(text=text, lang='en')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # HTML5 Autoplay
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.markdown(md, unsafe_allow_html=True)

# =========================
# 📸 VIDEO PROCESSING
# =========================
class OCRProcessor(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # Store the live frame in session state for the OCR to grab
        st.session_state["live_frame"] = img
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# =========================
# 🚀 STREAMLIT UI
# =========================
st.set_page_config(page_title="Mobile Book Reader", layout="centered")
st.title("📱 Mobile Book Reader")
st.write("Align the book text in the video below.")
s
# 1. Start Video Stream (Uses Back Camera)
webrtc_ctx = webrtc_streamer(
    key="mobile-ocr",
    video_processor_factory=OCRProcessor,*
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={
        "video": {"facingMode": "environment"}, # FORCES BACK CAMERA
        "audio": False
    },
)

# 2. Trigger Recognition
if webrtc_ctx.state.playing:
    # Big button for easy thumb-pressing on mobile
    if st.button("📖 READ THIS PAGE", use_container_width=True):
        if "live_frame" in st.session_state:
            with st.spinner("🧠 Analyzing Book..."):
                img = st.session_state["live_frame"]
                # Run the pretrained model
                results = reader.readtext(img, detail=0)
                full_text = " ".join(results)
                
                if full_text.strip():
                    st.success(f"Detected: {full_text}")
                    speak(full_text)
                else:
                    st.warning("No text detected. Get closer!")**