import openai
import streamlit as st
import os
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile
from datetime import date

# API anahtarı
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Log klasörü
log_dir = tempfile.mkdtemp(prefix="vision_chat_")

# Chat başlat
chat = VisionChatWithMemory(log_dir=log_dir)

# ====================== GÜNLÜK STREAK ======================
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_used_date" not in st.session_state:
    st.session_state.last_used_date = None

today = date.today()

# Streak kontrolü
if st.session_state.last_used_date != today:
    if st.session_state.last_used_date is not None:
        if (today - st.session_state.last_used_date).days > 1:
            st.session_state.streak = 0  # Seri kırıldı
    st.session_state.last_used_date = today

# ====================== TEMA ======================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Sağ üst tema butonu
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
        }
        .theme-toggle:hover { background: rgba(255,255,255,0.1); }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("🌙" if st.session_state.dark_mode else "☀️", 
             key="theme_btn", 
             help="Tema değiştir"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# Tema stili
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
            .stApp { background-color: #0f172a; color: #f3f4f6; }
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stFileUploader > div {
                background-color: #1e2937; color: #f3f4f6; border: 1px solid #475569;
            }
            .stButton > button { background-color: #4f46e5; color: white; }
            .stButton > button:hover { background-color: #6366f1; }
            h1, h2, h3, p, div, label { color: #f3f4f6 !important; }
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
        </style>
        """,
        unsafe_allow_html=True
    )

st.set_page_config(page_title="Akıllı Matematik Yardımcısı", layout="centered")

# ====================== BAŞLIK + STREAK ======================
col_title, col_streak = st.columns([4, 1])

with col_title:
    st.title("Akıllı Matematik Yardımcısı")

with col_streak:
    if st.session_state.streak > 0:
        st.markdown(f"**🔥 {st.session_state.streak} Gün**")
    else:
        st.markdown("**🔥 Seri Başlasın!**")

st.markdown("🔥 Sor, çöz, kazan! | 🧠 İstersen cevabını da kontrol ettir!")

# Güvenli Session State
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

# Soruyu Çöz butonu
if st.button("Soruyu Çöz", type="primary"):
    if not st.session_state.question.strip() and image is None:
        st.warning("Lütfen soru yazın veya görsel yükleyin.")
    else:
        with st.spinner("Çözülüyor..."):
            try:
                answer = chat.ask_new_question(st.session_state.question, image=image)
                st.subheader("Cevap")
                st.markdown(LatexNodes2Text().latex_to_text(answer))
                
                # Streak Güncelle
                if st.session_state.last_used_date != today:
                    st.session_state.streak += 1
                st.session_state.last_used_date = today
                
            except Exception as e:
                st.error(f"Hata: {str(e)}")

# Kendi cevabını kontrol ettir
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
                - Doğruysa tebrik et ve kısa açıklama yap.
                - Yanlışsa neden yanlış olduğunu net açıkla.
                Cevabı kısa tut.
                """

                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400
                )
                
                result = response.choices[0].message.content
                st.session_state.control_result = result
                
                # Streak Güncelle
                if st.session_state.last_used_date != today:
                    st.session_state.streak += 1
                st.session_state.last_used_date = today
                
            except Exception as e:
                st.error(f"Kontrol hatası: {str(e)}")

if st.session_state.control_result:
    st.subheader("Kontrol Sonucu")
    st.markdown(st.session_state.control_result)

if st.button("Tümünü Temizle"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")
st.markdown("**Her soru bir zaferdir – devam et! 💪**")

st.markdown(
    """
    <p style="text-align: center; color: #94a3b8; font-style: italic; font-size: 0.95rem; margin-top: 8px;">
        ━━━ Bu AI alfa sürümündedir, hata yapabilir. ━━━
    </p>
    """,
    unsafe_allow_html=True
)
