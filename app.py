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
if "current_summary" not in st.session_state:
    st.session_state.current_summary = None

today = date.today()

# ====================== TEMA VE SAYFA ======================
st.set_page_config(page_title="Ders Yardımcım - Akıllı Eğitim Asistanı", layout="centered", page_icon="🎓")

if st.session_state.dark_mode:
    st.markdown("""<style>.stApp { background-color: #0f172a; color: #f3f4f6; }</style>""", unsafe_allow_html=True)

# ====================== MÜFREDAT VERİ YAPISI ======================
CURRICULUM = {
    "İlkokul (1-4. Sınıf)": {
        "Matematik": ["Temel Dört İşlem", "Kesirler", "Zaman ve Ölçme", "Temel Geometri", "Veri Toplama"],
        "Türkçe": ["Okuduğunu Anlama", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam", "Cümlede Anlam"],
        "Fen Bilimleri": ["Canlılar Dünyası", "Maddeyi Tanıyalım", "Kuvvet ve Hareket", "Dünyamız ve Gökyüzü"],
        "Sosyal Bilgiler": ["Birey ve Toplum", "Kültür ve Miras", "Üretim, Tüketim ve Dağıtım", "Etkin Vatandaşlık"]
    },
    "Ortaokul (5-7. Sınıf)": {
        "Matematik": ["Oran-Orantı", "Yüzdeler", "Tam Sayılar", "Cebirsel İfadeler", "Geometrik Cisimler", "Veri Analizi"],
        "Türkçe": ["Paragrafta Anlam", "Fiiller ve Ek Fiil", "Söz Sanatları", "Yazım ve Noktalama", "Metin Türleri"],
        "Fen Bilimleri": ["Hücre ve Bölünmeler", "Kuvvet ve Enerji", "Maddenin Tanecikli Yapısı", "Işık ve Ses", "Sistemler"],
        "Sosyal Bilgiler": ["Tarihe Yolculuk", "İnsanlar, Yerler ve Çevreler", "Bilim, Teknoloji ve Toplum", "Küresel Bağlantılar"],
        "İngilizce": ["Vocabulary & Grammar", "Reading Comprehension", "Daily Expressions"]
    },
    "8. Sınıf (LGS)": {
        "Matematik": ["Çarpanlar ve Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Basit Olayların Olasılığı", "Cebirsel İfadeler", "Doğrusal Denklemler", "Eşitsizlikler", "Üçgenler", "Dönüşüm Geometrisi"],
        "Türkçe": ["Fiilimsiler", "Sözcükte ve Cümlede Anlam", "Paragrafta Anlam", "Cümlenin Ögeleri", "Fiilde Çatı", "Cümle Türleri", "Yazım-Noktalama", "Metin Türleri"],
        "Fen Bilimleri": ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri"],
        "T.C. İnkılap Tarihi": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Milli Bir Destan: Ya İstiklal Ya Ölüm", "Atatürkçülük ve Çağdaşlaşan Türkiye"],
        "İngilizce": ["Friendship", "Teen Life", "In the Kitchen", "On the Phone", "The Internet", "Adventures", "Tourism"]
    },
    "9. Sınıf": {
        "Matematik": ["Mantık", "Kümeler", "Denklem ve Eşitsizlikler", "Üçgenler", "Veri"],
        "Fizik": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Hareket ve Kuvvet", "Enerji", "Isı ve Sıcaklık"],
        "Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", "Maddenin Halleri"],
        "Biyoloji": ["Yaşam Bilimi Biyoloji", "Hücre", "Canlılar Dünyası"],
        "Türk Dili ve Edebiyatı": ["Giriş ve Metin Türleri", "Hikaye", "Şiir", "Masal / Fabl", "Roman"],
        "Tarih": ["Tarih ve Zaman", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya", "İlk ve Orta Çağlarda Türk Dünyası"],
        "Coğrafya": ["Doğal Sistemler", "Beşeri Sistemler", "Bölgeler ve Ülkeler", "Çevre ve Toplum"]
    },
    "10. Sınıf": {
        "Matematik": ["Sayma ve Olasılık", "Fonksiyonlar", "Polinomlar", "İkinci Dereceden Denklemler", "Dörtgenler ve Çokgenler", "Uzay Geometri"],
        "Fizik": ["Elektrik ve Manyetizma", "Basınç ve Kaldırma Kuvveti", "Dalgalar", "Optik"],
        "Kimya": ["Kimyanın Temel Kanunları", "Karışımlar", "Asitler, Bazlar ve Tuzlar", "Kimya Her Yerde"],
        "Biyoloji": ["Mitoz ve Mayoz Bölünme", "Kalıtımın Genel İlkeleri", "Ekosistem Ekolojisi ve Güncel Çevre Sorunları"],
        "Türk Dili ve Edebiyatı": ["Tanzimat Edebiyatı", "Servet-i Fünun ve Fecr-i Ati", "Milli Edebiyat", "Şiir, Tiyatro ve Roman"],
        "Tarih": ["Yerleşme ve Devletleşme Sürecinde Selçuklu", "Beylikten Devlete Osmanlı", "State & Society in Ottoman"],
        "Coğrafya": ["Kayaçlar ve Yeryüzü Şekilleri", "Su, Toprak ve Bitki Varlığı", "Nüfus ve Yerleşme"]
    },
    "11. Sınıf": {
        "Matematik": ["Trigonometri", "Analitik Geometri", "Fonksiyonlarda Uygulamalar", "Denklem ve Eşitsizlik Sistemleri", "Çember ve Daire", "Uzay Geometri"],
        "Fizik": ["Vektörler ve Kuvvet", "Bir ve İki Boyutta Hareket", "Newton'ın Hareket Yasaları", "İş, Güç, Enerji", "Atışlar", "Elektrik ve Magnetizma"],
        "Kimya": ["Modern Atom Teorisi", "Gazlar", "Sıvı Çözeltiler", "Kimyasal Tepkimelerde Enerji", "Tepkime Hızları ve Denge"],
        "Biyoloji": ["İnsan Fizyolojisi (Sinir, Destek, Sindirim, Dolaşım, Solunum, Üriner Sistemler)", "Komünite ve Popülasyon Ekolojisi"],
        "Türk Dili ve Edebiyatı": ["Tanzimat'tan Cumhuriyet'e Türk Edebiyatı", "Şiir, Makale, Sohbet, Fıkra", "Roman ve Hikaye"],
        "Tarih": ["18. ve 19. Yüzyıl Osmanlı Tarihi", "Uluslararası İlişkilerde Denge Stratejisi", "Devrimler Çağında Değişen Devlet-Toplum"]
    },
    "12. Sınıf / YKS": {
        "Matematik": ["LİMİT ve Süreklilik", "TÜREV ve Uygulamaları", "İNTEGRAL ve Uygulamaları", "Logaritma", "Diziler", "Dönüşümler Geometrisi"],
        "Fizik": ["Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği", "Atom Fiziğine Giriş ve Radyoaktivite", "Modern Fizik"],
        "Kimya": ["Kimya ve Elektrik", "Karbon Kimyasına Giriş", "Organik Bileşikler (Alkan, Alken, Alkin, Alkol, Ester vb.)"],
        "Biyoloji": ["Genden Proteine", "Canlılarda Enerji Dönüşümleri (Fotosentez, Kemosentez, Hücresel Solunum)", "Bitki Biyolojisi"],
        "Türk Dili et Edebiyatı": ["Cumhuriyet Dönemi Türk Edebiyatı", "Dünya Edebiyatı", "Metin İncelemeleri"],
        "Tarih": ["20. Yüzyıl Başlarında Dünya ve Osmanlı", "Atatürkçülük ve Türk İnkılabı", "II. Dünya Savaşı ve Soğuk Savaş Dönemi"]
    },
    "Üniversite": {
        "Matematik / Kalkülüs": ["Limit ve Süreklilik", "Türev ve Uygulamaları", "İntegral Teknikleri", "Çok Değişkenli Fonksiyonlar", "Dizi ve Seriler"],
        "Lineer Cebir": ["Matrisler ve Determinant", "Vektör Uzayları", "Özdeğer ve Özvektörler", "Lineer Dönüşümler"],
        "Fizik (Mekanik / Elektrik)": ["Newton Yasaları", "İş, Enerji ve Momentum", "Elektriksel Alan ve Potansiyel", "Gauss Yasası ve Manyetizma"],
        "Programlama / Yazılım": ["Algoritmalar ve Akış Şemaları", "Veri Yapıları", "Nesne Yönelimli Programlama", "Temel Python/C++"]
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

# AI Sorgu Fonksiyonu (Türkiye Yüzyılı Maarif Modeli ve MEB Müfredatına Uyumlu)
def ask_gemini(prompt_text):
    sys_instruction = (
        f"Sen 'Ders Yardımcım' platformunda görevli uzman bir öğretmen ve eğitim koçusun. "
        f"Öğrencinin okuduğu seviye: '{selected_grade}'. Ders: '{selected_subject}'. Konu: '{selected_topic}'. "
        f"Anlatım dilini, kavram seviyesini ve çözümlerini Türkiye Yüzyılı Maarif Modeli ve MEB güncel müfredat esaslarına tam uyumlu yap. "
        f"Soruları ve özetleri adım adım, açık, motive edici ve anlaşılır bir dille anlat."
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

# Seçim Durumu ve Hızlı Araçlar
if is_selection_complete:
    st.info(f"🎯 **Sınıf:** `{selected_grade}` | **Ders:** `{selected_subject}` | **Konu:** `{selected_topic}`")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📝 Konu Özeti Çıkar"):
            with st.spinner("Güncel MEB müfredatına göre özet hazırlanıyor..."):
                summary_prompt = (
                    f"Bana '{selected_topic}' konusuyla ilgili {selected_grade} seviyesinde "
                    f"Türkiye Yüzyılı Maarif Modeli esaslarına uygun şu 3 başlıktan oluşan akılda kalıcı bir ders özeti çıkar:\n"
                    f"1. 📌 Temel Kavramlar ve Formüller / Tanımlar\n"
                    f"2. ⚠️ Sınavda En Çok Yapılan Hatalar ve Tuzaklar\n"
                    f"3. 💡 Altın İpuçları ve Pratik Taktikler"
                )
                st.session_state.current_summary = ask_gemini(summary_prompt)

    with col_btn2:
        generate_quiz = st.button("🧪 Mini Test Oluştur (3 Soru)")

else:
    st.warning("⚠️ Lütfen sağ menüden **Sınıf**, **Ders** ve **Konu** seçimi yapınız.")
    generate_quiz = False

# ====================== AÇILIR-KAPANIR ÖZET ALANI ======================
if st.session_state.current_summary and is_selection_complete:
    with st.expander(f"📌 {selected_topic} - Konu Özeti Kartı (Okumak/Kapatmak İçin Tıklayın)", expanded=True):
        st.markdown(st.session_state.current_summary)
        
        # İndirme Butonu
        st.download_button(
            label="📥 Özeti Not Olarak İndir (.txt)",
            data=st.session_state.current_summary,
            file_name=f"{selected_subject}_{selected_topic}_Ozeti.txt",
            mime="text/plain"
        )

# Geçmiş Mesajlar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Soru veya Test İşleme
prompt_to_send = None
if generate_quiz:
    prompt_to_send = f"Bana '{selected_topic}' konusuyla ilgili {selected_grade} seviyesine uygun güncel müfredata göre 3 adet çoktan seçmeli soru hazırla. Cevap anahtarını ve detaylı çözümleri en alta ekle."
elif user_input := st.chat_input("Sorunuzu buraya yazın..."):
    if not is_selection_complete:
        st.error("Lütfen önce sağ menüden seçim yapın!")
    else:
        prompt_to_send = user_input

if prompt_to_send:
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    with st.spinner("Ders Yardımcım yanıtlıyor..."):
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
    st.session_state.current_summary = None
    st.rerun()
