import openai
import streamlit as st
import os
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile

# API anahtarı Secrets'ten geliyor
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Log klasörü (geçici)
log_dir = tempfile.mkdtemp(prefix="vision_chat_")

# Chat başlat
chat = VisionChatWithMemory(log_dir=log_dir)

# Koyu gri arka plan + beyaz yazı + temiz stil
st.markdown(
    """
    <style>
        .stApp {
            background-color: #1f2937;           /* koyu gri arka plan */
            color: #f3f4f6;                      /* açık beyaz-gri yazı */
        }
        .stTextInput > div > div > input {
            background-color: #374151;
            color: #f3f4f6;
            border: 1px solid #4b5563;
        }
        .stFileUploader > div {
            background-color: #374151;
            color: #f3f4f6;
            border: 1px solid #4b5563;
        }
        .stButton > button {
            background-color: #4f46e5;           /* indigo buton */
            color: white;
            border: none;
        }
        .stButton > button:hover {
            background-color: #6366f1;
        }
        h1, h2, h3, p, div, label, .stWarning, .stError, .stSuccess {
            color: #f3f4f6 !important;
        }
        header {
            background-color: #1f2937 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #111827;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Lise Matematik Yardımcısı", layout="centered")

# Başlık ve kısa motivasyon cümleleri (sadece emoji)
st.title("Lise Matematik Yardımcısı")
st.markdown("🔥 Sor, çöz, kazan!")
st.markdown("🧠 Beynin en iyi antrenmanı matematik!")
st.markdown("💪 Her soru bir zafer adımıdır!")

st.markdown("---")

# Session state
if "question" not in st.session_state:
    st.session_state.question = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Soru alanı
st.session_state.question = st.text_input(
    "Sorunuzu buraya yazın",
    value=st.session_state.question,
    placeholder="Örn: 2x + 5 = 13 çöz"
)

# Görsel yükleme
uploaded_image = st.file_uploader(
    "Soru görselini yükle (isteğe bağlı)",
    type=["png", "jpg", "jpeg"]
)

image = None
if uploaded_image is not None:
    st.session_state.uploaded_image = uploaded_image
    image = Image.open(uploaded_image)
    st.image(image, caption="Yüklenen Görsel")

# Butonlar
col1, col2 = st.columns(2)

with col1:
    if st.button("Soruyu Çöz", type="primary"):
        if not st.session_state.question.strip() and image is None:
            st.warning("Lütfen soru yazın veya görsel yükleyin.")
        else:
            with st.spinner("Düşünüyor... 🤔"):
                try:
                    answer = chat.ask_new_question(st.session_state.question, image=image)
                    st.subheader("Cevap")
                    st.markdown(LatexNodes2Text().latex_to_text(answer))
                    st.success("🚀 Harika iş!")
                except Exception as e:
                    st.error(f"Hata: {str(e)}")

with col2:
    if st.button("Temizle"):
        st.session_state.clear()
        st.rerun()

# Alt kısımda küçük motivasyon cümleleri
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>"
            "🔥 Her deneme seni güçlendirir</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1rem; color: #9ca3af;'>"
            "🧩 Bir sonraki soru seni bekliyor!</p>", unsafe_allow_html=True)
