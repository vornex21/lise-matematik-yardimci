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

# Koyu gri arka plan + beyaz yazı
st.markdown(
    """
    <style>
        .stApp { background-color: #1f2937; color: #f3f4f6; }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stFileUploader > div {
            background-color: #374151; color: #f3f4f6; border: 1px solid #4b5563;
        }
        .stButton > button { background-color: #4f46e5; color: white; border: none; }
        .stButton > button:hover { background-color: #6366f1; }
        h1, h2, h3, p, div, label { color: #f3f4f6 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Akıllı Matematik Rehberi", layout="centered")

st.title("Akıllı Matematik Rehberi")
st.markdown("🔥 Sor, çöz, kazan! | 🧠 Cevabını kontrol ettir!")

# Session state
if "question" not in st.session_state:
    st.session_state.question = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""
if "control_result" not in st.session_state:
    st.session_state.control_result = None

# Soru girişi
st.session_state.question = st.text_input("Sorunuzu buraya yazın", value=st.session_state.question)
uploaded_image = st.file_uploader("Görsel yükle (isteğe bağlı)", type=["png", "jpg", "jpeg"])

image = None
if uploaded_image is not None:
    st.session_state.uploaded_image = uploaded_image
    image = Image.open(uploaded_image)
    st.image(image, caption="Yüklenen Görsel")

# Kullanıcının cevabı + kontrol butonu
st.markdown("### Senin Cevabın")
st.session_state.user_answer = st.text_area("Cevabını buraya yaz", 
                                            value=st.session_state.user_answer, 
                                            height=150,
                                            placeholder="Örn: x = 4")

if st.button("Cevabımı Kontrol Et", type="primary"):
    if not st.session_state.question.strip() and image is None:
        st.warning("Lütfen önce soru yazın veya görsel yükleyin.")
    elif not st.session_state.user_answer.strip():
        st.warning("Cevabınızı yazmadınız!")
    else:
        with st.spinner("Cevabını kontrol ediyorum... 🧐"):
            try:
                # GPT'ye soruyu + kullanıcının cevabını gönderiyoruz
                prompt = f"""
                Soru: {st.session_state.question}
                Kullanıcının cevabı: {st.session_state.user_answer}

                Bu cevap doğru mu? 
                - Doğruysa tebrik et ve kısa bir açıklama yap.
                - Yanlışsa neden yanlış olduğunu net bir şekilde açıkla.
                - Matematiksel ifadeleri LaTeX formatında tut.
                Cevabı kısa ve net tut.
                """
                
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                
                result = response.choices[0].message.content
                st.session_state.control_result = result
                
            except Exception as e:
                st.error(f"Kontrol sırasında hata: {str(e)}")

# Kontrol sonucunu göster
if st.session_state.control_result:
    st.subheader("Kontrol Sonucu")
    st.markdown(st.session_state.control_result)

# Temizle butonu
if st.button("Tümünü Temizle"):
    st.session_state.clear()
    st.rerun()

# Alt motivasyon
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>"
            "🔥 Her kontrol seni bir adım ileriye taşır!</p>", unsafe_allow_html=True)
