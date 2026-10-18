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
        "
