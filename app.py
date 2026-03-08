import openai
import streamlit as st
import os
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile

# API anahtarı (Secrets'ten çekiliyor)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Log klasörü (Cloud için geçici)
log_dir = tempfile.mkdtemp(prefix="vision_chat_")

# Chat nesnesini başlat
chat = VisionChatWithMemory(log_dir=log_dir)

# Tam siyah arka plan + beyaz yazılar + kontrastlı stil
st.markdown(
    """
    <style>
        .stApp {
            background-color: #000000;  /* Tam siyah arka plan */
            color: #ffffff;             /* Tüm yazılar beyaz */
        }
        .stTextInput > div > div > input,
        .stFileUploader > div,
        .stButton > button {
            background-color: #1a1a1a;  /* Koyu gri kutular */
            color: #ffffff;
            border: 1px solid #4a5568;
        }
        .stButton > button:hover {
            background-color: #2d3748;
        }
        h1, h2, h3, p, div, span, label, .stWarning, .stError, .stSuccess {
            color: #ffffff !important;
        }
        header, [data-testid="stHeader"] {
            background-color: #000000 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sayfa başlığı
st.set_page_config(page_title="Lise Matematik Yardımcısı 📚", layout="wide")

# Üstte büyük pi resmi (senin yüklediğin birinci resim)
st.image("pi sayisi", use_column_width=True)

st.markdown("<h1 style='text-align: center;'>Lise Matematik Yardımcısı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem;'>Birlikte her soruyu çözeriz! 🚀</p>", unsafe_allow_html=True)

# Yanlara küçük resimler (senin yüklediğin diğerleri)
col_left, col_mid, col_right = st.columns([1, 4, 1])
with col_left:
    st.image("sekiller", width=150)  # Karmaşık şekiller
with col_right:
    st.image("yazi tahtasi", width=150)  # Yazı tahtası

st.markdown("---")

# Session state
if "question" not in st.session_state:
    st.session_state.question = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Girişler
st.session_state.question = st.text_input("**Sorunuzu buraya yazın**", 
                                          value=st.session_state.question, 
                                          placeholder="Örn: 2x + 5 = 13 çöz")

uploaded_image = st.file_uploader("**Soru görselini yükle (isteğe bağlı)**", type=["png", "jpg", "jpeg"])

image = None
if uploaded_image is not None:
    st.session_state.uploaded_image = uploaded_image
    image = Image.open(uploaded_image)
    st.image(image, caption="**Yüklenen Görsel**", use_column_width=True)

# Butonlar
col1, col2 = st.columns(2)

with col1:
    if st.button("**Soruyu Çöz**", type="primary"):
        if not st.session_state.question.strip() and image is None:
            st.warning("Lütfen soru yazın veya görsel yükleyin.")
        else:
            with st.spinner("Düşünüyor... 🤔"):
                try:
                    answer = chat.ask_new_question(st.session_state.question, image=image)
                    st.subheader("**Cevap**")
                    st.markdown(LatexNodes2Text().latex_to_text(answer))
                    st.success("Harika! Başka soru var mı? 😄")
                except Exception as e:
                    st.error(f"Hata: {str(e)}")

with col2:
    if st.button("**Temizle**"):
        st.session_state.clear()
        st.rerun()

# Alt kısım – motive edici yazı
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>"
            "Her soru bir zaferdir – devam et! 💪</p>", 
            unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #a0aec0;'>"
            "Yapay zeka ile hazırlanmıştır • Soru sor, birlikte öğrenelim!</p>", 
            unsafe_allow_html=True)
