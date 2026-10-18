import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import os
from datetime import date
from PyPDF2 import PdfReader

# ====================== GEMINI CLIENT ======================
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if api_key:
    if "gemini_client" not in st.session_state:
        st.session_state.gemini_client = genai.Client(api_key=api_key)
else:
    st.error("🔑 API Anahtarı bulunamadı! Lütfen Streamlit Secrets alanına 'GEMINI_API_KEY' anahtarını ekleyin.")

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

# ====================== TAM MÜFREDAT VERİ YAPISI ======================
CURRICULUM = {
    "İlkokul (1-4. Sınıf)": {
        "Matematik": [
            "Doğal Sayılar ve Toplama-Çıkarma",
            "Çarpma ve Bölme İşlemleri",
            "Kesirler ve Zaman Ölçme",
            "Geometrik Cisimler ve Şekiller",
            "Uzunluk, Tartma ve Sıvı Ölçme",
            "Veri Toplama ve Değerlendirme"
        ],
        "Türkçe": [
            "Okuduğunu Anlama ve Yorumlama",
            "Sözcükte ve Cümlede Anlam",
            "Yazım Kuralları ve Noktalama İşaretleri",
            "Metin Türleri ve Şiir",
            "Görsel Okuma ve Grafikler"
        ],
        "Fen Bilimleri": [
            "Yer Kabuğu ve Dünyamızın Yapısı",
            "Canlılar Dünyasına Yolculuk",
            "Kuvvetin Etkileri ve Hareket",
            "Maddenin Özellikleri ve Halleri",
            "Aydınlatma ve Ses Teknolojileri",
            "İnsan ve Çevre İlişkisi",
            "Basit Elektrik Devreleri"
        ],
        "Sosyal Bilgiler": [
            "Birey ve Toplum (Herkesin Bir Öyküsü Var)",
            "Kültür ve Miras (Ailem, Geçmişim)",
            "İnsanlar, Yerler ve Çevreler (Yaşadığımız Yer)",
            "Üretim, Tüketim ve Dağıtım",
            "Etkin Vatandaşlık ve Haklarımız",
            "Küresel Bağlantılar"
        ]
    },
    "Ortaokul (5-7. Sınıf)": {
        "Matematik": [
            "Doğal Sayılar ve Kesirlerle İşlemler",
            "Ondalık Gösterim ve Yüzdeler",
            "Tam Sayılar ve Cebirsel İfadeler",
            "Oran ve Orantı",
            "Doğrular, Açılar ve Çokgenler",
            "Çember, Daire ve Alan Ölçme",
            "Veri Analizi ve Veri İşleme"
        ],
        "Türkçe": [
            "Sözcükte, Cümlede ve Paragrafta Anlam",
            "Fiiller, Ek Fiil ve Fiilde Yapı",
            "Söz Sanatları ve Metin Türleri",
            "Yazım Kuralları ve Noktalama İşaretleri",
            "Sözel Mantık ve Görsel Okuma"
        ],
        "Fen Bilimleri": [
            "Güneş, Dünya ve Ay Sistemi",
            "Hücre, Büyüme ve Bölünmeler",
            "Kuvvet, İş ve Enerji Dönüşümleri",
            "Maddenin Tanecikli Yapısı ve Isı",
            "Işığın Yayılması, Yansıması ve Soğurulması",
            "Canlılarda Üreme, Büyüme ve Gelişme",
            "Elektrik Devreleri"
        ],
        "Sosyal Bilgiler": [
            "Birey ve Toplum (Sosyal Rollerin Değişimi)",
            "Kültür ve Miras (Tarihe Yolculuk)",
            "İnsanlar, Yerler ve Çevreler (Türkiye Coğrafyası)",
            "Bilim, Teknoloji ve Toplum",
            "Üretim, Dağıtım ve Tüketim",
            "Etkin Vatandaşlık (Yönetim Şekilleri)",
            "Küresel Bağlantılar"
        ],
        "İngilizce": [
            "Appearance and Personality",
            "Sports and Daily Routines",
            "Biographies and Past Events",
            "Wild Animals and Nature",
            "Television, Media and Environment",
            "Parties, Celebrations and Holidays"
        ]
    },
    "8. Sınıf (LGS)": {
        "Matematik": [
            "Çarpanlar ve Katlar (EBOB-EKOK)",
            "Üslü İfadeler ve Bilimsel Gösterim",
            "Kareköklü İfadeler",
            "Veri Analizi (Grafik Türleri)",
            "Basit Olayların Olma Olasılığı",
            "Cebirsel İfadeler ve Özdeşlikler",
            "Doğrusal Denklemler ve Eğim",
            "Eşitsizlikler",
            "Üçgenler ve Eşlik-Benzerlik",
            "Dönüşüm Geometrisi ve Geometrik Cisimler"
        ],
        "Türkçe": [
            "Fiilimsiler (Eylemsiler)",
            "Sözcükte, Cümlede ve Paragrafta Anlam",
            "Cümlenin Ögeleri",
            "Fiilde Çatı",
            "Cümle Türleri",
            "Yazım Kuralları ve Noktalama İşaretleri",
            "Metin Türleri ve Söz Sanatları",
            "Sözel Mantık ve Muhakeme"
        ],
        "Fen Bilimleri": [
            "Mevsimler ve İklim",
            "DNA ve Genetik Kod",
            "Basınç (Katı, Sıvı, Gaz)",
            "Madde ve Endüstri (Periyodik Sistem, Tepkimeler)",
            "Basit Makineler",
            "Enerji Dönüşümleri ve Çevre Bilimi",
            "Elektrik Yükleri ve Elektrik Enerjisi"
        ],
        "T.C. İnkılap Tarihi": [
            "Bir Kahraman Doğuyor (Atatürk'ün Hayatı)",
            "Milli Uyanış: Bağımsızlık Yolunda Atılan Adımlar",
            "Milli Bir Destan: Ya İstiklal Ya Ölüm!",
            "Atatürkçülük ve Çağdaşlaşan Türkiye",
            "Demokratikleşme Çabaları",
            "Atatürk Dönemi Türk Dış Politikası",
            "Atatürk'ün Ölümü ve Sonrası"
        ],
        "İngilizce": [
            "Unit 1: Friendship",
            "Unit 2: Teen Life",
            "Unit 3: In the Kitchen",
            "Unit 4: On the Phone",
            "Unit 5: The Internet",
            "Unit 6: Adventures",
            "Unit 7: Tourism",
            "Unit 8: Chores",
            "Unit 9: Science",
            "Unit 10: Natural Forces"
        ]
    },
    "9. Sınıf": {
        "Matematik": [
            "Mantık (Önermeler ve Bileşik Önermeler)",
            "Kümeler ve Küme İşlemleri",
            "Denklem ve Eşitsizlikler",
            "Üçgenlerde Açı, Eşlik ve Benzerlik",
            "Üçgenlerin Yardımcı Elemanları ve Dik Üçgen",
            "Üçgenin Alanı ve Trigonometriye Giriş",
            "Veri (Merkezi Eğilim ve Yayılım Ölçüleri)"
        ],
        "Fizik": [
            "Fizik Bilimine Giriş",
            "Madde ve Özellikleri (Özkütle, Dayanıklılık)",
            "Hareket ve Kuvvet (Newton Yasaları)",
            "İş, Güç ve Enerji",
            "Isı ve Sıcaklık (Genleşme)",
            "Elektrostatik"
        ],
        "Kimya": [
            "Kimya Bilimi ve Simyadan Kimyaya",
            "Atom ve Periyodik Sistem",
            "Kimyasal Türler Arası Etkileşimler",
            "Maddenin Halleri (Gazlar, Sıvılar, Katılar)",
            "Doğa ve Kimya"
        ],
        "Biyoloji": [
            "Yaşam Bilimi Biyoloji (Canlıların Temel Bileşenleri)",
            "Hücre (Hücre Zarı, Organeller ve Taşıma)",
            "Canlılar Dünyası ve Sınıflandırma"
        ],
        "Türk Dili ve Edebiyatı": [
            "Giriş (Edebiyatın Sanatla ve Bilimle İlişkisi)",
            "Hikaye (Olay ve Durum Hikayesi)",
            "Şiir (Nazım Hikmet, Ahenk Unsurları)",
            "Masal ve Fabl",
            "Roman",
            "Tiyatro",
            "Biyografi / Otobiyografi"
        ],
        "Tarih": [
            "Tarih ve Zaman",
            "İnsanlığın İlk Dönemleri",
            "Orta Çağ'da Dünya",
            "İlk ve Orta Çağlarda Türk Dünyası",
            "İslam Medeniyetinin Doğuşu",
            "Türklerin İslamiyet'i Kabulü ve İlk Türk İslam Devletleri"
        ],
        "Coğrafya": [
            "Doğal Sistemler (Doğa, İnsan, Harita Bilgisi)",
            "Dünya'nın Şekli ve Hareketleri",
            "İklim Bilgisi (Sıcaklık, Basınç, Rüzgarlar, Nem)",
            "Beşeri Sistemler (Yerleşme)",
            "Bölgeler ve Ülkeler",
            "Çevre ve Toplum"
        ]
    },
    "10. Sınıf": {
        "Matematik": [
            "Sayma ve Olasılık (Permütasyon, Kombinasyon, Binom)",
            "Fonksiyonlar ve Fonksiyon Grafikleri",
            "Polinomlar ve Çarpanlara Ayırma",
            "İkinci Dereceden Denklemler ve Karmaşık Sayılar",
            "Dörtgenler ve Çokgenler",
            "Uzay Geometri (Prizmalar ve Piramitler)"
        ],
        "Fizik": [
            "Elektrik ve Manyetizma (Devreler, Mıknatıs)",
            "Basınç ve Kaldırma Kuvveti",
            "Dalgalar (Yay, Su, Ses ve Işık Dalgaları)",
            "Optik (Aydınlanma, Aynalar, Kırılma, Mercekler)"
        ],
        "Kimya": [
            "Kimyanın Temel Kanunları ve Mol Kavramı",
            "Tepkime Türleri ve Kimyasal Hesaplamalar",
            "Karışımlar ve Çözeltiler",
            "Asitler, Bazlar ve Tuzlar",
            "Kimya Her Yerde"
        ],
        "Biyoloji": [
            "Hücre Bölünmeleri (Mitoz ve Mayoz)",
            "Eşeyli ve Eşeysiz Üreme",
            "Kalıtımın Genel İlkeleri (Mendel Genetiği)",
            "Ekosistem Ekolojisi ve Güncel Çevre Sorunları"
        ],
        "Türk Dili ve Edebiyatı": [
            "Giriş ve Türk Edebiyatının Dönemleri",
            "Hikaye (Dede Korkut, Halk Hikayesi, Tanzimat)",
            "Şiir (İslamiyet Öncesi, Divan, Halk Şiiri)",
            "Destan ve Efsane",
            "Roman (Tanzimat, Servet-i Fünun, Milli Edebiyat)",
            "Tiyatro",
            "Anı (Hatıra) ve Haber Metinleri"
        ],
        "Tarih": [
            "Yerleşme ve Devletleşme Sürecinde Selçuklu",
            "Beylikten Devlete Osmanlı Siyaseti",
            "Devletleşme Sürecinde Savaşçılar ve Askerler",
            "Beylikten Devlete Osmanlı Medeniyeti",
            "Dünya Gücü Osmanlı (1453-1595)",
            "Sultan ve Osmanlı Merkez Teşkilatı"
        ],
        "Coğrafya": [
            "Dünya'nın Tektonik Oluşumu ve Kayaçlar",
            "İç ve Dış Kuvvetler",
            "Türkiye'de Yer Şekilleri ve Su / Toprak / Bitki Varlığı",
            "Nüfusun Gelişimi, Dağılışı ve Piramitler",
            "Küresel Hatlar ve Ulaşım Yolları",
            "Afetler"
        ]
    },
    "11. Sınıf": {
        "Matematik": [
            "Trigonometri (Yönlü Açılar, Fonksiyonlar, Teoremler)",
            "Analitik Geometri (Nokta ve Doğrunun Analitiği)",
            "Fonksiyonlarda Uygulamalar ve Dönüşümler",
            "İkinci Dereceden İki Bilinmeyenli Denklem ve Eşitsizlik Sistemleri",
            "Çember ve Daire (Açı, Teğet, Dairenin Alanı)",
            "Uzay Geometri (Silindir, Konu, Küre)",
            "Olasılık (Koşullu Olasılık ve Deneysel/Teorik Olasılık)"
        ],
        "Fizik": [
            "Vektörler ve Bağıl Hareket",
            "Newton'ın Hareket Yasaları ve Tork/Denge",
            "Bir ve İki Boyutta Sabit İvmeli Hareket (Atışlar)",
            "İş, Güç, Enerji ve İtme-Momentum",
            "Elektriksel Kuvvet, Potansiyel ve Paralel Levhalar",
            "Manyetizma ve Elektromanyetik İndüksiyon",
            "Alternatif Akım ve Transformatörler"
        ],
        "Kimya": [
            "Modern Atom Teorisi ve Kuantum Sayıları",
            "Periyodik Sistem ve Özellikleri",
            "Gazlar (Gaz Yasaları ve İideal Gaz)",
            "Sıvı Çözeltiler ve Derişim Birimleri",
            "Kimyasal Tepkimelerde Enerji (Entalpi)",
            "Tepkime Hızları ve Kimyasal Denge",
            "Asit-Baz Dengesi ve Çözünürlük Dengesi (KÇÇ)"
        ],
        "Biyoloji": [
            "Denetleyici ve Düzenleyici Sistemler (Sinir ve Endokrin)",
            "Duyu Organları",
            "Destek ve Hareket Sistemi",
            "Sindirim Sistemi",
            "Dolaşım ve Lenf Sistemi (Bağışıklık)",
            "Solunum Sistemi",
            "Üriner (Boşaltım) Sistem ve Üreme Sistemi",
            "Komünite ve Popülasyon Ekolojisi"
        ],
        "Türk Dili ve Edebiyatı": [
            "Giriş (Edebiyat ve Toplum İlişkisi)",
            "Hikaye (Cumhuriyet Dönemi Hikayesi)",
            "Şiir (Tanzimat'tan Cumhuriyet'e Şiir Akımları)",
            "Makale, Sohbet ve Fıkra",
            "Roman (Milli Edebiyat ve Cumhuriyet İlk Yılları)",
            "Tiyatro",
            "Eleştiri ve Mülakat/Röportaj"
        ],
        "Tarih": [
            "17. Yüzyılda Değişen Dünya ve Osmanlı",
            "18. Yüzyılda Uluslararası İlişkilerde Denge Stratejisi",
            "Devrimler Çağında Değişen Devlet-Toplum İlişkileri",
            "19. Yüzyıl Sermaye ve Emek",
            "19. ve 20. Yüzyılda Toplumsal Hayattaki Değişimler"
        ]
    },
    "12. Sınıf / YKS": {
        "Matematik": [
            "Üstel ve Logaritmik Fonksiyonlar",
            "Gerçek Sayı Dizileri (Aritmetik ve Geometrik Dizi)",
            "Trigonometri (Toplam-Fark ve Yarım Açı Formülleri)",
            "Dönüşümler Geometrisi",
            "Fonksiyonlarda Limit ve Süreklilik",
            "Türev (Türev Alma Kuralları, Teğet ve Maks-Min Problemleri)",
            "İntegral (Belirsiz-Belirli İntegral ve Alan Hesabı)",
            "Çemberin Analitik İncelemesi"
        ],
        "Fizik": [
            "Düzgün Çembersel Hareket ve Açısal Momentum",
            "Kütle Çekim Yasaları ve Kepler Yasaları",
            "Basit Harmonik Hareket",
            "Dalga Mekaniği (Kırınım, Girişim ve Doppler)",
            "Elektromanyetik Dalgalar",
            "Atom Fiziğine Giriş ve Radyoaktivite",
            "Modern Fizik (Rölativite, Fotoelektrik, Compton)",
            "Modern Fiziğin Teknolojideki Uygulamaları"
        ],
        "Kimya": [
            "Kimya ve Elektrik (Redoks, İndirgenme-Yükseltgenme)",
            "Elektrotlar ve Elektrokimyasal Piller (Galvanik/Elektroliz)",
            "Karbon Kimyasına Giriş (Hibritleşme ve Molekül Geometrisi)",
            "Organik Bileşikler: Hidrokarbonlar (Alkan, Alken, Alkin)",
            "Organik Bileşikler: Fonksiyonel Gruplar (Alkol, Eter, Aldehit, Keton, Karboksilik Asit, Ester)"
        ],
        "Biyoloji": [
            "Nükleik Asitler (DNA ve RNA'nın Yapısı)",
            "Genetik Şifre ve Protein Sentezi",
            "Canlılarda Enerji Dönüşümleri (Fotosentez ve Kemosentez)",
            "Hücresel Solunum (Oksijenli ve Oksijensiz Solunum, Fermentasyon)",
            "Bitki Biyolojisi (Bitkisel Dokular, Organlar, Taşıma ve Üreme)",
            "Canlılar ve Çevre"
        ],
        "Türk Dili ve Edebiyatı": [
            "Giriş (Edebiyat ve Felsefe/Psikoloji)",
            "Hikaye (1980 Sonrası Türk Hikayesi)",
            "Şiir (Cumhuriyet Dönemi Saf Şiir, Toplumcu Şiir, Garip, İkinci Yeni vb.)",
            "Roman (Cumhuriyet Dönemi Romanı - Bireyin İç Dünyası, Toplumcu, Modernist)",
            "Tiyatro (Cumhuriyet Dönemi Tiyatrosu)",
            "Deneme ve Söylev (Nutuk)"
        ],
        "Tarih": [
            "20. Yüzyıl Başlarında Osmanlı Devleti ve Dünya",
            "Milli Mücadele (Hazırlık, Cepheler ve Antlaşmalar)",
