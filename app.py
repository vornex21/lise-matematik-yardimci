import streamlit as st
from PIL import Image
from vision_chat import VisionChatWithMemory
from pylatexenc.latex2text import LatexNodes2Text
import tempfile
import openai
from datetime import date
from PyPDF2 import PdfReader

# ====================== OPENAI CLIENT ======================
if "openai_client" not in st.session_state:
    st.session_state.openai_client = openai.OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

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
    st.title(" ")
    
    st.subheader("🤖 AI Modeli")
    model_options = ["gpt-4o-mini", "gpt-4o"]
    selected_model = st.selectbox("Model Seç", model_options, index=0)
    st.session_state.selected_model = selected_model

    st.subheader("📚 Ders")
    subjects = ["Genel Matematik", "Cebir", "Geometri", "Türev ve İntegral", "Olasılık"]
    selected_subject = st.selectbox("Konu Seç", subjects, index=0)
    st.session_state.current_subject = selected_subject

    st.markdown("---")
    st.metric("🔥 Streak", f"{st.session_state.streak} Gün")

# ====================== ANA EKRAN ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🧠 Akıllı Matematik Yardımcısı")
with col2:
    if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("**Adım adım çözümler • Görsel + PDF destekli**")

# Sohbet Geçmişi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(LatexNodes2Text().latex_to_text(message["content"]))

# Soru Girişi
if prompt := st.chat_input("Matematik sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Çözülüyor..."):
        try:
            image = Image.open(st.session_state.uploaded_file) if st.session_state.uploaded_file and isinstance(st.session_state.uploaded_file, Image.Image) else None

            answer = chat.ask_new_question(
                question=prompt,
                image=image,
                model=st.session_state.selected_model,
                subject=st.session_state.current_subject
            )

            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(LatexNodes2Text().latex_to_text(answer))

            if st.session_state.last_used_date != today:
                st.session_state.streak += 1
                st.session_state.last_used_date = today

        except Exception as e:
            st.error(f"Hata: {str(e)}")

# ====================== DOSYA YÜKLEME (Görsel + PDF) ======================
with st.expander("📄 PDF veya Görsel Yükle"):
    uploaded_file = st.file_uploader("PDF veya resim yükleyin", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        
        if uploaded_file.type == "application/pdf":
            st.success("PDF yüklendi. İçeriğini okumak için soru sorabilirsiniz.")
            # PDF Önizleme (ilk sayfadan metin)
            try:
                reader = PdfReader(uploaded_file)
                first_page_text = reader.pages[0].extract_text()[:300]  # İlk 300 karakter
                st.text_area("PDF'ten çıkarılan metin (örnek)", first_page_text, height=150)
            except:
                st.warning("PDF metni okunamadı.")
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Yüklenen Görsel", width=400)

# Temizle Butonu
if st.button("🗑️ Sohbeti Temizle"):
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.rerun()

st.markdown("---")
st.markdown("**Her soru bir zaferdir! Devam et 💪**")
