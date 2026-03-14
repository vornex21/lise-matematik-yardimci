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

# Tema seçimi (session_state ile kalıcı olsun)
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # varsayılan koyu mod

# Tema stilini uygula
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
            .stApp { background-color: #1f2937; color: #f3f4f6; }
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stFileUploader > div {
                background-color: #374151; color: #f3f4f6; border: 1px solid #4b5563;
            }
            .stButton > button { background-color: #4f46e5; color: white; }
            .stButton > button:hover { background-color: #6366f1; }
            h1, h2, h3, p, div, label { color: #f3f4f6 !important; }
            header { background-color: #1f2937 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
            .stApp { background-color: #ffffff; color: #111827; }
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stFileUploader > div {
                background-color: #f9fafb; color: #111827; border: 1px solid #d1d5db;
            }
            .stButton > button { background-color: #3b82f6; color: white; }
            .stButton > button:hover { background-color: #2563eb; }
            h1, h2, h3, p, div, label { color: #111827 !important; }
            header { background-color: #ffffff !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

# Sağ üst köşede küçük yuvarlak tema değiştirme butonu (sadece emoji)
st.markdown(
    """
    <style>
        .theme-toggle {
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 9999;
            background: transparent;
            border: none;
            font-size: 28px;
            cursor: pointer;
            padding: 8px 12px;
            border-radius: 50%;
            transition: background 0.3s;
        }
        .theme-toggle:hover {
            background: rgba(255,255,255,0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Buton (emoji moduna göre değişir)
if st.button("🌙" if st.session_state.dark_mode else "☀️", 
             key="theme_btn", 
             help="Tema değiştir", 
             use_container_width=False):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

st.set_page_config(page_title="Lise Matematik Yardımcısı", layout="centered")

st.title("Lise Matematik Yardımcısı")
st.markdown("🔥 Sor, çöz, kazan!")

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
st.session_state.question = st.text_input("Sorunuzu buraya yazın", 
                                          value=st.session_state.question,
                                          placeholder="Örn: 2x + 5 = 13 çöz")

uploaded_image = st.file_uploader("Görsel yükle (isteğe bağlı)", type=["png", "jpg", "jpeg"])

image = None
if uploaded_image is not None:
    st.session_state.uploaded_image = uploaded_image
    image = Image.open(uploaded_image)
    st.image(image, caption="Yüklenen Görsel")

# “Soruyu Çöz” butonu
if st.button("Soruyu Çöz", type="primary"):
    if not st.session_state.question.strip() and image is None:
        st.warning("Lütfen soru yazın veya görsel yükleyin.")
    else:
        with st.spinner("Çözülüyor..."):
            try:
                answer = chat.ask_new_question(st.session_state.question, image=image)
                st.subheader("Cevap")
                st.markdown(LatexNodes2Text().latex_to_text(answer))
            except Exception as e:
                st.error(f"Hata: {str(e)}")

# Opsiyonel: Cevap kontrol kısmı
st.markdown("### İstersen kendi cevabını kontrol ettir")
st.session_state.user_answer = st.text_area("Kendi cevabını buraya yaz", 
                                            value=st.session_state.user_answer,
                                            height=100,
                                            placeholder="Örn: x = 4")

if st.button("Cevabımı Kontrol Et"):
    if not st.session_state.question.strip() and image is None:
        st.warning("Önce soru yazın veya görsel yükleyin.")
    elif not st.session_state.user_answer.strip():
        st.warning("Cevabınızı yazmadınız!")
    else:
        with st.spinner("Cevabınızı kontrol ediyorum... 🧐"):
            try:
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
                    max_tokens=400
                )
                
                result = response.choices[0].message.content
                st.session_state.control_result = result
                
            except Exception as e:
                st.error(f"Kontrol hatası: {str(e)}")

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
st.markdown("Her soru bir zaferdir – devam et! 💪")
