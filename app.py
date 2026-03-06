import openai
import streamlit as st
import os
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile

# API anahtarı (Streamlit Secrets'ten çekiliyor)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Log klasörü (Cloud için geçici klasör)
log_dir = tempfile.mkdtemp(prefix="vision_chat_")

# Chat nesnesini başlat
chat = VisionChatWithMemory(log_dir=log_dir)

# Streamlit arayüz ayarları
st.set_page_config(page_title="📚 Lise Matematik Yardımcısı 📊", layout="wide")  # wide yaptık ki yanlara yer olsun

# Sayfanın üstüne büyük hoş geldin resmi ve yazı
st.image(
    "https://images.unsplash.com/photo-1509228627929-8243eb4676d2?auto=format&fit=crop&q=80&w=2000",
    caption="Matematik seni bekliyor! 🚀",
    use_column_width=True
)

st.markdown("<h1 style='text-align: center; color: #1e40af;'>📚 Lise Matematik Yardımcısı 📊</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem;'>Bir soru yaz, fotoğraf yükle... Birlikte çözeriz! 😊</p>", unsafe_allow_html=True)

# Yanlara küçük matematik ikon/resim ekleme (columns ile)
col_left, col_mid, col_right = st.columns([1, 4, 1])

with col_left:
    st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&q=80&w=400", 
             caption="Formüller", width=150)

with col_right:
    st.image("https://images.unsplash.com/photo-1581092160560-1c1d2b2e3e1c?auto=format&fit=crop&q=80&w=400", 
             caption="Başarı", width=150)

# Orta kısım - ana içerik
st.markdown("---")

# Session state başlatma
if "question" not in st.session_state:
    st.session_state.question = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Soru girişi (orta kısımda)
st.session_state.question = st.text_input("**Sorunuzu buraya yazın**", 
                                          value=st.session_state.question, 
                                          key="question_input",
                                          placeholder="Örn: 2x + 5 = 13 çöz")

uploaded_image = st.file_uploader("**Soru görselini yükle (isteğe bağlı)**", 
                                  type=["png", "jpg", "jpeg"], 
                                  key="file_uploader")

image = None
if uploaded_image is not None:
    st.session_state.uploaded_image = uploaded_image

if st.session_state.uploaded_image:
    image = Image.open(st.session_state.uploaded_image)
    st.image(image, caption="**Yüklenen Görsel**", use_container_width=True)

# Butonlar (orta kısımda)
col1, col2 = st.columns(2)

with col1:
    if st.button("**Soruyu Çöz**", type="primary"):  # primary buton daha dikkat çeker
        if not st.session_state.question.strip() and image is None:
            st.warning("Lütfen bir soru yazın veya görsel yükleyin.")
        else:
            with st.spinner("Düşünüyor... 🤔"):
                try:
                    answer = chat.ask_new_question(st.session_state.question, image=image)
                    st.subheader("**Cevap**")
                    st.markdown(LatexNodes2Text().latex_to_text(answer))
                    st.success("Harika! Bir soru daha mı var? 😄")
                except Exception as e:
                    st.error(f"Hata oluştu: {str(e)}")

with col2:
    if st.button("**Temizle**", type="secondary"):
        st.session_state.clear()
        st.rerun()

# Sayfanın altına motive edici yazı ve resim
st.markdown("---")

st.image("https://images.unsplash.com/photo-1516979187457-637a1ec45b07?auto=format&fit=crop&q=80&w=1000", 
         caption="Her soru bir zaferdir – devam et! 💪", 
         use_column_width=True)

st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #4b5563;'>"
            "Matematik zor değil, sadece doğru bakış açısı lazım. Sen başaracaksın! 🌟</p>", 
            unsafe_allow_html=True)

# En alta küçük bir not
st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #6b7280;'>"
            "Yapay zeka ile hazırlanmıştır • Soru sor, birlikte öğrenelim!</p>", 
            unsafe_allow_html=True)
