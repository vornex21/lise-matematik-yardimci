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
