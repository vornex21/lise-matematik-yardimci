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

# Koyu gri arka plan + beyaz yazı (önceki stilin korunması)
st.markdown(
    """
    <style>
        .stApp {
            background-color: #1f2937;
            color: #f3f4f6;
        }
        .stTextInput > div > div > input,
        .stFileUploader > div,
        .stButton > button {
            background-color: #374151;
            color: #f3f4f6;
            border: 1px solid #4b5563;
        }
        .stButton > button:hover {
            background-color: #4f46e5;
        }
        h1, h2, h3, p, div, label {
            color: #f3f4f6 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Lise Matematik Yardımcısı", layout="centered")

# Sekmeler oluştur
tab1, tab2 = st.tabs(["Soru Çöz", "Analiz"])

with tab1:
    st.title("Soru Çöz")
    st.markdown("🔥 Sor, çöz, kazan!")

    # Session state (sadece bu sekme için)
    if "question" not in st.session_state:
        st.session_state.question = ""
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None

    st.session_state.question = st.text_input("Sorunuzu buraya yazın", value=st.session_state.question)
    uploaded_image = st.file_uploader("Görsel yükle (isteğe bağlı)", type=["png", "jpg", "jpeg"])

    image = None
    if uploaded_image:
        st.session_state.uploaded_image = uploaded_image
        image = Image.open(uploaded_image)
        st.image(image, caption="Yüklenen Görsel")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Soruyu Çöz"):
            if not st.session_state.question.strip() and image is None:
                st.warning("Lütfen soru yazın veya görsel yükleyin.")
            else:
                with st.spinner("Düşünüyor... 🤔"):
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

with tab2:
    st.title("Analiz")
    st.markdown("🧠 İstatistikler ve analizler burada! 📊")

    # Basit analiz örnekleri (gerçek verilerle genişletebilirsin)
    st.markdown("**Son 5 soru istatistiği**")
    st.markdown("Doğru cevap: 4/5 (80%)")
    st.markdown("En çok çözülen konu: Denklem çözme")
    st.markdown("En uzun süre düşündüğün soru: 45 saniye")

    # Motivasyon cümleleri (emoji ile)
    st.markdown("🔥 Sen bu işi biliyorsun!")
    st.markdown("🚀 Her soru seni daha güçlü yapıyor!")
    st.markdown("💡 Bir sonraki zafer senin!")

    # İleride buraya grafik ekleyebilirsin (örneğin matplotlib ile)
    st.markdown("(İleride buraya başarı grafiği eklenebilir)")

# Alt kısım (ortak motivasyon)
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>Her soru bir zaferdir – devam et! 💪</p>", unsafe_allow_html=True)
