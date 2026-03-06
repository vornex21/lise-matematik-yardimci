import openai
import streamlit as st
import os
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile

# API anahtarı
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Log klasörü
log_dir = tempfile.mkdtemp(prefix="vision_chat_")

# Chat başlat
chat = VisionChatWithMemory(log_dir=log_dir)

# CSS ile arka plan ve stil
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f0f4f8;  /* Açık mavi-gri arka plan */
            background-image: linear-gradient(to bottom right, #e0f2fe, #f0f9ff);
        }
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            border-radius: 8px;
        }
        h1, h2, h3 {
            color: #1d4ed8;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sayfa başlığı
st.set_page_config(page_title="Lise Matematik Yardımcısı 📚", layout="wide")

# Üstte büyük resim + yazı
st.image(
    "https://images.unsplash.com/photo-1509228627929-8243eb4676d2?auto=format&fit=crop&q=80&w=2000",
    use_column_width=True
)
st.markdown("<h1 style='text-align: center;'>Lise Matematik Yardımcısı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem;'>Birlikte her soruyu çözeriz! 🚀</p>", unsafe_allow_html=True)

# Yanlara küçük resimler
col_left, col_mid, col_right = st.columns([1, 4, 1])
with col_left:
    st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&q=80&w=400", width=150)
with col_right:
    st.image("https://images.unsplash.com/photo-1581092160560-1c1d2b2e3e1c?auto=format&fit=crop&q=80&w=400", width=150)

# Ana içerik
st.markdown("---")

# Session state
if "question" not in st.session_state:
    st.session_state.question = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Girişler
st.session_state.question = st.text_input("Sorunuz:", value=st.session_state.question)
uploaded_image = st.file_uploader("Görsel yükle (isteğe bağlı)", type=["png", "jpg", "jpeg"])

image = None
if uploaded_image:
    st.session_state.uploaded_image = uploaded_image
    image = Image.open(uploaded_image)
    st.image(image, caption="Yüklenen Görsel", use_column_width=True)

# Butonlar
col1, col2 = st.columns(2)
with col1:
    if st.button("Soruyu Çöz"):
        if not st.session_state.question.strip() and image is None:
            st.warning("Lütfen soru yazın veya görsel yükleyin.")
        else:
            with st.spinner("Düşünüyor..."):
                try:
                    answer = chat.ask_new_question(st.session_state.question, image=image)
                    st.subheader("Cevap")
                    st.markdown(LatexNodes2Text().latex_to_text(answer))
                except Exception as e:
                    st.error(f"Hata: {str(e)}")

with col2:
    if st.button("Temizle"):
        st.session_state.clear()
        st.rerun()

# Alt kısım
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>Her soru bir zaferdir – devam et! 💪</p>", unsafe_allow_html=True)
st.image(
    "https://images.unsplash.com/photo-1516979187457-637a1ec45b07?auto=format&fit=crop&q=80&w=1000",
    caption="Başarı seninle! 🌟",
    use_column_width=True
)
