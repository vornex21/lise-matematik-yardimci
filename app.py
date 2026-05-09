import streamlit as st
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile
import openai
from datetime import date

# ==================== OPENAI AYARI ====================
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Log klasörü
log_dir = tempfile.mkdtemp(prefix="vision_chat_")

chat = VisionChatWithMemory(log_dir=log_dir)

# ====================== STREAK SİSTEMİ ======================
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_used_date" not in st.session_state:
    st.session_state.last_used_date = None

today = date.today()

# ====================== TEMA ======================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

st.markdown(
    """
    <style>
        .theme-toggle {
            position: fixed; top: 15px; right: 15px; z-index: 9999;
            background: transparent; border: none; font-size: 28px;
            cursor: pointer; padding: 8px 12px; border-radius: 50%;
        }
        .theme-toggle:hover { background: rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True
)

if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

if st.session_state.dark_mode:
    st.markdown("""<style>.stApp { background-color: #0f172a; color: #f3f4f6; }</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Akıllı Matematik Yardımcısı", layout="centered")

col1, col2 = st.columns([4, 1])
with col1:
    st.title("Akıllı Matematik Yardımcısı")
with col2:
    st.markdown(f"### {'🔥' if st.session_state.streak > 0 else '⚪'} {st.session_state.streak} Gün")

st.markdown("🔥 Sor, çöz, kazan! | 🧠 İstersen cevabını da kontrol ettir!")

# Session State
for key in ["question", "user_answer", "control_result"]:
    if key not in st.session_state:
        st.session_state[key] = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

st.session_state.question = st.text_input("Sorunuzu buraya yazın", 
                                          value=st.session_state.question,
                                          placeholder="Örn: 2x + 5 = 13 çöz")

uploaded_image = st.file_uploader("Görsel yükle (isteğe bağlı)", type=["png", "jpg", "jpeg"])
image = Image.open(uploaded_image) if uploaded_image else None
if image:
    st.image(image, caption="Yüklenen Görsel")

# ====================== SORUYU ÇÖZ ======================
if st.button("Soruyu Çöz", type="primary"):
    if not st.session_state.question.strip() and image is None:
        st.warning("Lütfen soru yazın veya görsel yükleyin.")
    else:
        with st.spinner("Çözülüyor..."):
            try:
                answer = chat.ask_new_question(st.session_state.question, image=image)
                st.subheader("Cevap")
                st.markdown(LatexNodes2Text().latex_to_text(answer))
                
                if st.session_state.last_used_date != today:
                    st.session_state.streak += 1
                st.session_state.last_used_date = today
            except Exception as e:
                st.error(f"Hata: {str(e)}")

# ====================== CEVAP KONTROL ======================
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
        with st.spinner("Kontrol ediliyor..."):
            try:
                prompt = f"""
                Soru: {st.session_state.question}
                Kullanıcının cevabı: {st.session_state.user_answer}
                Bu cevap doğru mu? Doğruysa tebrik et, yanlışsa nedenini net açıkla.
                """
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400
                )
                st.session_state.control_result = response.choices[0].message.content
                
                if st.session_state.last_used_date != today:
                    st.session_state.streak += 1
                st.session_state.last_used_date = today
            except Exception as e:
                st.error(f"Hata: {str(e)}")

if st.session_state.get("control_result"):
    st.subheader("Kontrol Sonucu")
    st.markdown(st.session_state.control_result)

if st.button("Tümünü Temizle"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")
st.markdown("**Her soru bir zaferdir – devam et! 💪**")
st.markdown(
    """
    <p style="text-align: center; color: #94a3b8; font-style: italic;">
        ━━━ Bu AI alfa sürümündedir, hata yapabilir. ━━━
    </p>
    """, unsafe_allow_html=True
)
