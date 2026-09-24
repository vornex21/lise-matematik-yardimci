import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import os
from datetime import date
from PyPDF2 import PdfReader

# ====================== GEMINI CLIENT ======================
# Streamlit Secrets (Secrets alanından API Key alma)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if "gemini_client" not in st.session_state and api_key:
    st.session_state.gemini_client = genai.Client(api_key=api_key)

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
    st.session_state.selected_model = "gemini-2.5-flash"
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
    
    st.subheader("🤖 AI Modeli")
    model_options = ["gemini-2.5-flash", "gemini-2.5-pro"]
    selected_model = st.selectbox("Model Seç", model_options, index=0)
    st.session_state.selected_model = selected_model

    st.subheader("📚 Ders")
    subjects = ["Genel Matematik", "Cebir", "Geometri", "Türev ve İntegral", "Olasılık"]
    selected_subject = st.selectbox("Konu Seç", subjects, index=0)
    st.session_state.current_subject = selected_subject

    st.markdown("---")
    st.metric("🔥 Streak", f"{st.session_state.streak} Gün", delta="bugün aktif" if st.session_state.last_used_date == today else None)

# ====================== ANA EKRAN ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🧠 Akıllı Matematik Yardımcısı")
with col2:
    if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("**Adım adım çözümler • Görsel + PDF destekli**")

# Sohbet Geçmişini Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Soru Girişi
if prompt := st.chat_input("Matematik sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Çözülüyor..."):
        try:
            if "gemini_client" not in st.session_state or not st.session_state.gemini_client:
                st.error("API Anahtarı bulunamadı. Lütfen App Settings > Secrets bölümüne GEMINI_API_KEY eklediğinizden emin olun.")
                st.stop()

            # Gönderilecek İçerikleri Hazırlama
            contents = []
            
            # Sistem Yönlendirmesi
            sys_instruction = f"Sen uzman bir matematik öğretmenisin. Uzmanlık alanın: {st.session_state.current_subject}. Soruları adım adım ve anlaşılır biçimde çöz."

            # Dosya Yüklendiyse İçeriğe Ekleme
            if st.session_state.uploaded_file:
                if st.session_state.uploaded_file.type == "application/pdf":
                    reader = PdfReader(st.session_state.uploaded_file)
                    pdf_text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            pdf_text += extracted + "\n"
                    if pdf_text:
                        contents.append(f"Yüklenen PDF İçeriği:\n{pdf_text}")
                else:
                    img = Image.open(st.session_state.uploaded_file)
                    contents.append(img)

            # Kullanıcı Sorusu
            contents.append(prompt)

            # Gemini API Çağrısı
            response = st.session_state.gemini_client.models.generate_content(
                model=st.session_state.selected_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction
                )
            )

            answer = response.text
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            with st.chat_message("assistant"):
                st.markdown(answer)

            # Streak Mantığı
            if st.session_state.last_used_date != today:
                st.session_state.streak += 1
                st.session_state.last_used_date = today
                st.success("🔥 Streak'in arttı! Bugün de devam ettin.")

        except Exception as e:
            st.error(f"Hata: {str(e)}")

# ====================== DOSYA YÜKLEME ======================
with st.expander("📄 PDF veya Görsel Yükle"):
    uploaded_file = st.file_uploader("PDF veya resim yükleyin", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        
        if uploaded_file.type == "application/pdf":
            st.success("✅ PDF yüklendi")
            try:
                reader = PdfReader(uploaded_file)
                text_sample = reader.pages[0].extract_text()[:400]
                if text_sample:
                    st.text_area("PDF'ten çıkarılan örnek metin:", text_sample, height=120)
            except Exception:
                st.error("PDF okuma hatası")
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
