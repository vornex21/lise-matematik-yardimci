import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import os
from datetime import date
from PyPDF2 import PdfReader

# ====================== GEMINI CLIENT ======================
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
if "grade_level" not in st.session_state:
    st.session_state.grade_level = "10. Sınıf"
if "current_subject" not in st.session_state:
    st.session_state.current_subject = "Genel Matematik"
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.5-flash"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

today = date.today()

# ====================== TEMA VE SAYFA ======================
st.set_page_config(page_title="MatemAI - Sınıf Düzeyli Matematik Asistanı", layout="centered")

if st.session_state.dark_mode:
    st.markdown("""<style>.stApp { background-color: #0f172a; color: #f3f4f6; }</style>""", unsafe_allow_html=True)

# ====================== SINIF DÜZEYİ VE KONU HARİTASI ======================
SUBJECT_MAP = {
    "İlkokul (1-4. Sınıf)": ["Temel Dört İşlem", "Kesirler", "Zaman ve Ölçme", "Temel Geometri"],
    "Ortaokul (5-7. Sınıf)": ["Oran-Orantı", "Yüzdeler", "Tam Sayılar", "Cebirsel İfadeler", "Geometri"],
    "LGS Hazırlık (8. Sınıf)": ["Çarpanlar ve Katlar", "Üslü-Köklü İfadeler", "Olasılık", "Veri Analizi", "Eşitsizlikler"],
    "9. Sınıf": ["Mantık", "Kümeler", "Denklem ve Eşitsizlikler", "Üçgenler", "Veri"],
    "10. Sınıf": ["Sayma ve Olasılık", "Fonksiyonlar", "Polinomlar", "İkinci Dereceden Denklemler", "Dörtgenler"],
    "11. Sınıf": ["Trigonometri", "Analitik Geometri", "Fonksiyonlarda Uygulamalar", "Çember ve Daire", "Uzay Geometri"],
    "12. Sınıf / YKS": ["LİMİT ve Süreklilik", "TÜREV", "İNTEGRAL", "Trigonometri", "Logaritma", "Diziler"],
    "Üniversite": ["Lineer Cebir", "Calculus (Kalkülüs)", "Diferansiyel Denklemler", "Olasılık ve İstatistik"]
}

# ====================== SAĞ MENÜ / SIDEBAR ======================
with st.sidebar:
    st.title("🎓 Öğrenci Profili")
    
    # 1. Sınıf Düzeyi Seçimi
    selected_grade = st.selectbox(
        "🏫 Sınıf Düzeyinizi Seçin",
        list(SUBJECT_MAP.keys()),
        index=3  # Varsayılan: 9. Sınıf
    )
    st.session_state.grade_level = selected_grade

    # 2. Seçilen Sınıfa Göre Dinamik Konu Liste Seçimi
    available_subjects = SUBJECT_MAP[selected_grade]
    selected_subject = st.selectbox("📚 Konu / Ünite", available_subjects)
    st.session_state.current_subject = selected_subject

    st.markdown("---")
    st.subheader("⚙️ AI Ayarları")
    selected_model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-pro"], index=0)
    st.session_state.selected_model = selected_model

    st.markdown("---")
    st.metric("🔥 Streak", f"{st.session_state.streak} Gün", delta="bugün aktif" if st.session_state.last_used_date == today else None)

# ====================== ANA EKRAN ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🧠 MatemAI")
with col2:
    if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.info(f"🎯 **Aktif Seviye:** `{st.session_state.grade_level}` | **Konu:** `{st.session_state.current_subject}`")

# Geçmiş Mesajlar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Soru Girişi
if prompt := st.chat_input(f"{st.session_state.grade_level} düzeyindeki sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Çözülüyor..."):
        try:
            if "gemini_client" not in st.session_state or not st.session_state.gemini_client:
                st.error("API Anahtarı bulunamadı. Lütfen App Settings > Secrets kısmına GEMINI_API_KEY ekleyin.")
                st.stop()

            # Yapay Zekâya Verilecek Özel Rol ve Müfredat Talimatı
            sys_instruction = (
                f"Sen uzman bir matematik öğretmenisin. "
                f"Öğrencinin seviyesi: '{st.session_state.grade_level}'. "
                f"Şu anki konu: '{st.session_state.current_subject}'. "
                f"Anlatım dilini, karmaşıklığını ve terimleri tam olarak {st.session_state.grade_level} müfredat seviyesine uygun ayarla. "
                f"Soruyu adım adım, açık, teşvik edici ve anlaşılır şekilde çöz."
            )

            contents = []

            # Doküman / Görsel Ekleme
            if st.session_state.uploaded_file:
                if st.session_state.uploaded_file.type == "application/pdf":
                    reader = PdfReader(st.session_state.uploaded_file)
                    pdf_text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            pdf_text += extracted + "\n"
                    if pdf_text:
                        contents.append(f"Yüklenen Doküman İçeriği:\n{pdf_text}")
                else:
                    img = Image.open(st.session_state.uploaded_file)
                    contents.append(img)

            contents.append(prompt)

            # API Çağrısı
            response = st.session_state.gemini_client.models.generate_content(
                model=st.session_state.selected_model,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=sys_instruction)
            )

            answer = response.text
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            with st.chat_message("assistant"):
                st.markdown(answer)

            # Streak Sistemi
            if st.session_state.last_used_date != today:
                st.session_state.streak += 1
                st.session_state.last_used_date = today
                st.success("🔥 Streak'in arttı! Harika gidiyorsun.")

        except Exception as e:
            st.error(f"Hata Oluştu: {str(e)}")

# ====================== DOSYA YÜKLEME ======================
with st.expander("📄 Soru Fotoğrafı veya PDF Yükle"):
    uploaded_file = st.file_uploader("Dosya Seçin", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success("✅ Dosya eklendi")

if st.button("🗑️ Sohbeti Temizle"):
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.rerun()
