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
st.set_page_config(page_title="EduAI - Akıllı Eğitim Asistanı", layout="centered")

if st.session_state.dark_mode:
    st.markdown("""<style>.stApp { background-color: #0f172a; color: #f3f4f6; }</style>""", unsafe_allow_html=True)

# ====================== MÜFREDAT VE VERİ YAPISI ======================
# Yapı: Sınıf -> Ders -> Konular
CURRICULUM = {
    "İlkokul (1-4. Sınıf)": {
        "Matematik": ["Temel Dört İşlem", "Kesirler", "Zaman ve Ölçme", "Temel Geometri"],
        "Türkçe": ["Okuduğunu Anlama", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam"],
        "Fen Bilimleri": ["Canlılar Dünyası", "Maddeyi Tanıyalım", "Kuvvet ve Hareket", "Dünyamız ve Gökyüzü"],
        "Sosyal Bilgiler": ["Birey ve Toplum", "Kültür ve Miras", "Üretim, Tüketim ve Dağıtım"]
    },
    "Ortaokul (5-7. Sınıf)": {
        "Matematik": ["Oran-Orantı", "Yüzdeler", "Tam Sayılar", "Cebirsel İfadeler", "Geometri"],
        "Türkçe": ["Paragrafta Anlam", "Fiiller", "Söz Sanatları", "Yazım ve Noktalama"],
        "Fen Bilimleri": ["Hücre ve Bölünmeler", "Kuvvet ve Enerji", "Maddenin Tanecikli Yapısı", "Işık ve Ses"],
        "Sosyal Bilgiler": ["Tarihe Yolculuk", "İnsanlar, Yerler ve Çevreler", "Etkin Vatandaşlık"],
        "İngilizce": ["Grammar", "Vocabulary", "Reading Comprehension"]
    },
    "8. Sınıf (LGS)": {
        "Matematik": ["Çarpanlar ve Katlar", "Üslü-Köklü İfadeler", "Olasılık", "Cebirsel İfadeler", "Geometri"],
        "Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Metin Türleri", "Paragrafta Anlam"],
        "Fen Bilimleri": ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç", "Madde ve Endüstri"],
        "T.C. İnkılap Tarihi": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Milli Bir Destan: Ya İstiklal Ya Ölüm"],
        "İngilizce": ["Friendship", "Teen Life", "In the Kitchen", "On the Phone"]
    },
    "9. Sınıf": {
        "Matematik": ["Mantık", "Kümeler", "Denklem ve Eşitsizlikler", "Üçgenler"],
        "Fizik": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Hareket ve Kuvvet", "Enerji"],
        "Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler"],
        "Biyoloji": ["Yaşam Bilimi Biyoloji", "Hücre", "Canlılar Dünyası"],
        "Edebiyat": ["Giriş ve Metin Türleri", "Hikaye", "Şiir", "Roman"],
        "Tarih": ["Tarih ve Zaman", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya"],
        "Coğrafya": ["Doğal Sistemler", "Beşeri Sistemler", "Bölgeler ve Ülkeler"]
    },
    "10. Sınıf": {
        "Matematik": ["Sayma ve Olasılık", "Fonksiyonlar", "Polinomlar", "İkinci Dereceden Denklemler", "Dörtgenler"],
        "Fizik": ["Elektrik ve Manyetizma", "Dalgalar", "Optik"],
        "Kimya": ["Kimyanın Temel Kanunları", "Karışımlar", "Asitler, Bazlar ve Tuzlar"],
        "Biyoloji": ["Mitoz ve Mayoz Bölünme", "Kalıtımın Genel İlkeleri", "Ekosistem Ekolojisi"],
        "Edebiyat": ["Tanzimat Edebiyatı", "Servet-i Fünun", "Milli Edebiyat", "Şiir ve Roman Analysis"],
        "Tarih": ["Yerleşme ve Devletleşme Sürecinde Selçuklu", "Beylikten Devlete Osmanlı"],
        "Coğrafya": ["Kayaçlar ve Yeryüzü Şekilleri", "Su, Toprak ve Bitki Varlığı"]
    },
    "11. Sınıf": {
        "Matematik": ["Trigonometri", "Analitik Geometri", "Fonksiyonlarda Uygulamalar", "Çember ve Daire"],
        "Fizik": ["Vektörler ve Kuvvet", "Bir ve İki Boyutta Hareket", "Atışlar", "Elektrik ve Magnetizma"],
        "Kimya": ["Modern Atom Teorisi", "Gazlar", "Sıvı Çözeltiler", "Kimyasal Tepkimelerde Enerji ve Hız"],
        "Biyoloji": ["İnsan Fizyolojisi (Sistemler)", "Komünite ve Popülasyon Ekolojisi"],
        "Edebiyat": ["Tanzimat'tan Cumhuriyet'e Edebiyat", "Şiir", "Makale", "Sohbet"],
        "Tarih": ["18. ve 19. Yüzyıl Osmanlı Tarihi", "Uluslararası İlişkilerde Denge Stratejisi"]
    },
    "12. Sınıf / YKS": {
        "Matematik": ["LİMİT ve Süreklilik", "TÜREV", "İNTEGRAL", "Logaritma", "Diziler"],
        "Fizik": ["Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği", "Modern Fizik"],
        "Kimya": ["Kimya ve Elektrik", "Karbon Kimyasına Giriş", "Organik Bileşikler"],
        "Biyoloji": ["Genden Proteine", "Canlılarda Enerji Dönüşümleri (Fotosentez-Solunum)", "Bitki Biyolojisi"],
        "Edebiyat": ["Cumhuriyet Dönemi Türk Edebiyatı", "Dünya Edebiyatı"],
        "Tarih": ["20. Yüzyıl Başlarında Dünya", "Atatürkçülük ve Türk İnkılabı", "II. Dünya Savaşı"]
    },
    "Üniversite": {
        "Matematik / Kalkülüs": ["Limit ve Süreklilik", "Türev ve Uygulamaları", "İntegral Teknikleri", "Çok Değişkenli Fonksiyonlar"],
        "Lineer Cebir": ["Matrisler ve Determinant", "Vektör Uzayları", "Özdeğer ve Özvektörler"],
        "Fizik (Mekanik / Elektrik)": ["Newton Yasaları", "İş ve Enerji", "Elektriksel Alan ve Potansiyel"],
        "Programlama / Yazılım": ["Algoritmalar", "Veri Yapıları", "Nesne Yönelimli Programlama"]
    }
}

# ====================== SAĞ MENÜ / SIDEBAR ======================
with st.sidebar:
    st.title("🎓 Eğitim Profili")

    # 1. SINIF SEÇİMİ
    grade_options = ["-- Önce Sınıf Seçiniz --"] + list(CURRICULUM.keys())
    selected_grade = st.selectbox("🏫 Sınıf Düzeyi", grade_options, index=0)

    # 2. DERS SEÇİMİ (Sınıfa Göre Dinamik)
    if selected_grade == "-- Önce Sınıf Seçiniz --":
        selected_subject = st.selectbox("📚 Ders", ["-- Önce sınıf seçiniz --"], disabled=True)
        selected_topic = st.selectbox("📖 Konu / Ünite", ["-- Önce ders seçiniz --"], disabled=True)
    else:
        subject_options = ["-- Önce Ders Seçiniz --"] + list(CURRICULUM[selected_grade].keys())
        selected_subject = st.selectbox("📚 Ders", subject_options, index=0)

        # 3. KONU SEÇİMİ (Derse Göre Dinamik)
        if selected_subject == "-- Önce Ders Seçiniz --":
            selected_topic = st.selectbox("📖 Konu / Ünite", ["-- Önce ders seçiniz --"], disabled=True)
        else:
            topic_options = CURRICULUM[selected_grade][selected_subject]
            selected_topic = st.selectbox("📖 Konu / Ünite", topic_options, index=0)

    st.markdown("---")
    st.subheader("⚙️ AI Ayarları")
    selected_model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-pro"], index=0)

    st.markdown("---")
    st.metric("🔥 Streak", f"{st.session_state.streak} Gün", delta="bugün aktif" if st.session_state.last_used_date == today else None)

# ====================== ANA EKRAN ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🧠 EduAI")
with col2:
    if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Bilgi Çubuğu ve Seçim Kontrolü
is_selection_complete = (
    selected_grade != "-- Önce Sınıf Seçiniz --" and 
    selected_subject != "-- Önce Ders Seçiniz --"
)

if is_selection_complete:
    st.info(f"🎯 **Sınıf:** `{selected_grade}` | **Ders:** `{selected_subject}` | **Konu:** `{selected_topic}`")
else:
    st.warning("⚠️ Sorunuzu sormadan önce lütfen sağ menüden **Sınıf**, **Ders** ve **Konu** seçimi yapınız.")

# Geçmiş Mesajlar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Soru Girişi
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    if not is_selection_complete:
        st.error("Lütfen önce sağ menüden Sınıf Düzeyi ve Ders seçiminizi tamamlayın!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Çözülüyor ve açıklanıyor..."):
            try:
                if "gemini_client" not in st.session_state or not st.session_state.gemini_client:
                    st.error("API Anahtarı bulunamadı. Lütfen App Settings > Secrets kısmına GEMINI_API_KEY ekleyin.")
                    st.stop()

                # Yapay Zekâya Öğretmen Rolü Ve Özel Müfredat Talimatı
                sys_instruction = (
                    f"Sen uzman bir öğretmen ve eğitim danışmanısın. "
                    f"Öğrencinin okuduğu sınıf düzeyi: '{selected_grade}'. "
                    f"Ders: '{selected_subject}'. "
                    f"İlgili konu/ünite: '{selected_topic}'. "
                    f"Anlatım dilini, terim karmaşıklığını ve çözüm yöntemlerini TAM OLARAK '{selected_grade}' seviyesindeki '{selected_subject}' müfredatına uygun ayarla. "
                    f"Cevabı adım adım, motive edici ve öğrencinin anlayacağı en açık dille ver."
                )

                contents = []

                # PDF veya Görsel İçeriğini Ekleme
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
                    model=selected_model,
                    contents=contents,
                    config=types.GenerateContentConfig(system_instruction=sys_instruction)
                )

                answer = response.text
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                with st.chat_message("assistant"):
                    st.markdown(answer)

                # Streak Mantığı
                if st.session_state.last_used_date != today:
                    st.session_state.streak += 1
                    st.session_state.last_used_date = today
                    st.success("🔥 Streak'in arttı! Çalışmaya devam.")

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
