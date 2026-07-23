import streamlit as st
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile
import openai
from datetime import date

# ====================== OPENAI CLIENT ======================
if "openai_client" not in st.session_state:
    st.session_state.openai_client = openai.OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )
client = st.session_state.openai_client

# ====================== VISION CHAT ======================
if "log_dir" not in st.session_state:
    st.session_state.log_dir = tempfile.mkdtemp(prefix="math_chat_")

chat = VisionChatWithMemory(log_dir=st.session_state.log_dir)

# ====================== SESSION STATE ======================
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_used_date" not in st.session_state:
    st.session_state.last_used_date = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_subject" not in st.session_state:
    st.session_state.current_subject = "Genel Matematik"
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gpt-4o-mini"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

today = date.today()

# ====================== TEMA ======================
st.set_page_config(page_title="Akıllı Matematik Yardımcısı", layout="centered")

if st.session_state.dark_mode:
    st.markdown("""<style>.stApp { background-color: #0f172a; color: #f3f4f6; }</style>""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Ayarlar")
    
    # AI Model Seçimi
    st.subheader("🤖 AI Modeli")
    model_options = ["gpt-4o-mini", "gpt-4o"]
    selected_model = st.selectbox(
        "Model Seç", 
        model_options,
        index=model_options.index(st.session_state.selected_model)
    )
    st.session_state.selected_model = selected_model

    # Ders Seçimi
    st.subheader("📚 Ders")
    subjects = ["Genel Matematik", "Cebir", "Geometri", "Türev ve İntegral", "Olasılık"]
    selected_subject = st.selectbox(
        "Konu Seç", 
        subjects,
        index=subjects.index(st.session_state.current_subject)
    )
    st.session_state.current_subject = selected_subject

    st.markdown("---")
    st.metric("🔥 Streak", f"{st.session_state.streak} Gün")

# ====================== ANA UYGULAMA ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🧠 Akıllı Matematik Yardımcısı")
with col2:
    if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("**Adım adım çözümler • Görsel destekli**")

# Sohbet Geçmişi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(LatexNodes2Text().latex_to_text(message["content"]))

# Kullanıcı Soru Girişi
if prompt := st.chat_input("Matematik sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Çözülüyor..."):
        try:
            image = Image.open(st.session_state.uploaded_file) if st.session_state.uploaded_file else None

            answer = chat.ask_new_question(
                question=prompt,
                image=image,
                model=st.session_state.selected_model,
                subject=st.session_state.current_subject
            )

            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            with st.chat_message("assistant"):
                st.markdown(LatexNodes2Text().latex_to_text(answer))

            # Streak Güncelle
            if st.session_state.last_used_date != today:
                st.session_state.streak += 1
                st.session_state.last_used_date = today

        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

# Görsel Yükleme
with st.expander("📸 Görsel Yükle (İsteğe Bağlı)"):
    uploaded_file = st.file_uploader("Soru fotoğrafı yükleyin", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.image(uploaded_file, caption="Yüklenen Görsel", width=400)

# Temizle Butonu
if st.button("🗑️ Sohbeti Temizle"):
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.rerun()

st.markdown("---")
st.markdown("**Her soru bir zaferdir! Devam et 💪**")
