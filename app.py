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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

today = date.today()

# ====================== TEMA VE SAYFA ======================
st.set_page_config(page_title="Ders Yardımcım - Akıllı Eğitim Asistanı", layout="centered", page_icon="🎓")

if st.session_state.dark_mode:
    st.markdown("""<style>.stApp { background-color: #0f172a; color: #f3f4f6; }</style>""", unsafe_allow_html=True)

# ====================== MÜFREDAT VE VERİ YAPISI ======================
CURRICULUM = {
    "İlkokul (1-4. Sınıf)": {
        "Matematik": ["Temel Dört İşlem", "Kesirler", "Zaman ve Ölçme", "Temel Geometri"],
        "Türkçe": ["Okuduğunu Anlama", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam"],
        "Fen Bilimleri": ["Canlılar Dünyası", "Maddeyi Tanıyalım", "Kuvvet ve Hareket"]
    },
    "Ortaokul (5-7. Sınıf)": {
        "Matematik": ["Oran-Orantı", "Yüzdeler", "Tam Sayılar", "Cebirsel İfadeler"],
        "Türkçe": ["Paragrafta Anlam", "Fiiller", "Yazım ve Noktalama"],
        "Fen Bilimleri": ["Hücre ve Bölünmeler", "Kuvvet ve Enerji", "Işık ve Ses"]
    },
    "8. Sınıf (LGS)": {
        "Matematik": ["Çarpanlar ve Katlar", "Üslü-Köklü İfadeler", "Olasılık", "Eşitsizlikler"],
        "Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Paragrafta Anlam"],
        "Fen Bilimleri": ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç"]
    },
    "9. Sınıf": {
        "Matematik": ["Mantık", "Kümeler", "Denklem ve Eşitsizlikler", "Üçgenler"],
        "Fizik": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Hareket ve Kuvvet"],
        "Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem"],
        "Biyoloji": ["Yaşam Bilimi Biyoloji", "Hücre"]
    },
    "10. Sınıf": {
        "Matematik": ["Sayma ve Olasılık", "Fonksiyonlar", "Polinomlar", "İkinci Dereceden Denklemler"],
        "Fizik": ["Elektrik ve Manyetizma", "Optik"],
        "Kimya": ["Kimyanın Temel Kanunları", "Karışımlar"],
        "Biyoloji": ["Mitoz ve Mayoz Bölünme", "Kalıtımın Genel İlkeleri"]
    },
    "11. Sınıf": {
        "Matematik": ["Trigonometri", "Analitik Geometri", "Çember ve Daire"],
        "Fizik": ["Vektörler ve Kuvvet", "Atışlar", "Elektrik ve Magnetizma"],
        "Kimya": ["Modern Atom Teorisi", "Gazlar", "Sıvı Çözeltiler"]
    },
    "12. Sınıf / YKS": {
        "Matematik": ["LİMİT ve Süreklilik", "TÜREV", "İNTEGRAL", "Logaritma"],
        "Fizik": ["Çembersel Hareket", "Dalga Mekaniği", "Modern Fizik"],
        "Kimya": ["Kimya ve Elektrik", "Organik Bileşikler"]
    }
}

# ====================== SAĞ MENÜ / SIDEBAR ======================
with st.sidebar:
    st.title("🎓 Ders Yardımcım")

    # 1. SINIF SEÇİMİ
    grade_options = ["-- Önce Sınıf Seçiniz --"] + list(CURRICULUM.keys())
    selected_grade = st.selectbox("🏫 Sınıf Düzeyi", grade_options, index=0)

    # 2. DERS SEÇİMİ
    if selected_grade == "-- Önce Sınıf Seçiniz --":
        selected_subject = st.selectbox("📚 Ders", ["-- Önce sınıf seçiniz --"], disabled=True)
        selected_topic = st.selectbox("📖 Konu / Ünite", ["-- Önce ders seçiniz --"], disabled=True)
    else:
        subject_options = ["-- Önce Ders Seçiniz --"] + list(CURRICULUM[selected_grade].keys())
        selected_subject = st.selectbox("📚 Ders", subject_options, index=0)

        # 3. KONU SEÇİMİ
        if selected_subject == "-- Önce Ders Seçiniz --":
            selected_topic = st.selectbox("📖 Konu / Ünite", ["-- Önce ders seçiniz --"], disabled=True)
        else:
            topic_options = CURRICULUM[selected_grade][selected_subject]
            selected_topic = st.selectbox("📖 Konu / Ünite", topic_options, index=0)

    st.markdown("---")
    st.metric("🔥 Streak", f"{st.session_state.streak} Gün", delta="bugün aktif" if st.session_state.last_used_date == today else None)

# ====================== ANA EKRAN ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("📚 Ders Yardımcım")
with col2:
    if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

is_selection_complete = (
    selected_grade != "-- Önce Sınıf Seçiniz --" and 
    selected_subject != "-- Önce Ders Seçiniz --"
)

if is_selection_complete:
    st.info(f"🎯 **Sınıf:** `{selected_grade}` | **Ders:** `{selected_subject}` | **Konu:** `{selected_topic}`")
    
    # HIZLI ARAÇLAR (Özet ve Test Butonları)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        generate_summary = st.button("📝 Konu Özeti Çıkar")
    with col_btn2:
        generate_quiz = st.button("🧪 Mini Test Oluştur (3 Soru)")
else:
    st.warning("⚠️ Lütfen sağ menüden **Sınıf**, **Ders** ve **Konu** seçimi yapınız.")
    generate_summary = False
    generate_quiz = False

# Geçmiş Mesajlar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# AI Sorgu Fonksiyonu
def ask_gemini(prompt_text):
    sys_instruction = (
        f"Sen 'Ders Yardımcım' platformunda görevli uzman bir öğretmen ve eğitim koçusun. "
        f"Öğrencinin seviyesi: '{selected_grade}'. Ders: '{selected_subject}'. Konu: '{selected_topic}'. "
        f"Anlatım dilini ve örneklerini tam olarak bu sınıf düzeyine ve ders müfredatına uygun yap."
    )
    
    contents = []
    if st.session_state.uploaded_file:
        if st.session_state.uploaded_file.type == "application/pdf":
            reader = PdfReader(st.session_state.uploaded_file)
            pdf_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            contents.append(f"Yüklenen Doküman İçeriği:\n{pdf_text}")
        else:
            img = Image.open(st.session_state.uploaded_file)
            contents.append(img)

    contents.append(prompt_text)

    response = st.session_state.gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=sys_instruction)
    )
    return response.text

# Hızlı Araç Tetiklemeleri
prompt_to_send = None
if generate_summary:
    prompt_to_send = f"Bana '{selected_topic}' konusuyla ilgili akılda kalıcı, sınavda en çok çıkan yerleri içeren kısa bir çalışma özeti hazırla."
elif generate_quiz:
    prompt_to_send = f"Bana '{selected_topic}' konusuyla ilgili {selected_grade} seviyesine uygun 3 adet çoktan seçmeli soru hazırla. Cevap anahtarını en alta sakla."
elif user_input := st.chat_input("Sorunuzu buraya yazın..."):
    if not is_selection_complete:
        st.error("Lütfen önce sağ menüden seçim yapın!")
    else:
        prompt_to_send = user_input

if prompt_to_send:
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    with st.spinner("Ders Yardımcım hazırlanıyor..."):
        try:
            answer = ask_gemini(prompt_to_send)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

            if st.session_state.last_used_date != today:
                st.session_state.streak += 1
                st.session_state.last_used_date = today
                st.success("🔥 Streak'in arttı!")
        except Exception as e:
            st.error(f"Hata: {str(e)}")

# Dosya Yükleme ve Temizleme
with st.expander("📄 Soru Fotoğrafı veya PDF Yükle"):
    uploaded_file = st.file_uploader("Dosya Seçin", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success("✅ Dosya eklendi")

if st.button("🗑️ Sohbeti Temizle"):
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.rerun()
