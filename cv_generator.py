import streamlit as st
from fpdf import FPDF
import json
import os

# --- GÜVENLİ PDF SINIFI ---
class PDF(FPDF):
    def __init__(self, theme_color=(0, 0, 0)):
        super().__init__()
        self.theme_color = theme_color
        
        # Font kontrolü
        self.font_family_to_use = "helvetica" # Varsayılan font
        
        # Eğer arial.ttf varsa yükle, yoksa helvetica ile devam et (Çökmez/Boş kalmaz)
        if os.path.exists("arial.ttf"):
            try:
                self.add_font("ArialTR", "", "arial.ttf")
                self.add_font("ArialTR", "B", "arialbd.ttf" if os.path.exists("arialbd.ttf") else "arial.ttf")
                self.font_family_to_use = "ArialTR"
            except:
                pass

    def draw_section_header(self, title):
        self.ln(5)
        self.set_fill_color(*self.theme_color)
        self.set_text_color(255, 255, 255)
        self.set_font(self.font_family_to_use, "B", 12)
        self.cell(0, 8, f"  {title.upper()}", fill=True, ln=True, align="L")
        self.set_text_color(0, 0, 0)
        self.ln(2)

# --- ARAYÜZ ---
st.set_page_config(page_title="CV Generator", layout="wide")

# Veri Hazırlığı
if "cv_data" not in st.session_state:
    st.session_state["cv_data"] = {}
d = st.session_state["cv_data"]

# Sidebar ve Form Girişleri (Senin mevcut form yapın burada kalacak)
# ... (Form giriş kısımlarını buraya ekleyebilirsin, kısa tutmak için geçiyorum) ...
isim = st.text_input("Ad Soyad", d.get("isim", "Faruk Cinemre")) # Örnek olması için varsayılan ekledim
email = st.text_input("E-posta", d.get("email", ""))
telefon = st.text_input("Telefon", d.get("telefon", ""))
lokasyon = st.text_input("Lokasyon", d.get("lokasyon", ""))
ozet = st.text_area("Özet", d.get("ozet", ""))

tema_rengi = st.sidebar.color_picker("Tema Rengi", "#003366")
hex_color = tema_rengi.lstrip('#')
rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# --- PDF OLUŞTURMA ---
if st.button("✨ CV'Yİ PDF OLARAK OLUŞTUR"):
    if not isim:
        st.error("Ad Soyad boş olamaz!")
    else:
        pdf = PDF(theme_color=rgb_color)
        pdf.add_page()
        
        # Header
        pdf.set_font(pdf.font_family_to_use, "B", 24)
        pdf.set_text_color(*rgb_color)
        pdf.cell(0, 12, isim, ln=True)
        
        pdf.set_font(pdf.font_family_to_use, "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 5, f"{lokasyon} | {telefon} | {email}", ln=True)
        
        if ozet:
            pdf.draw_section_header("Profil")
            pdf.set_font(pdf.font_family_to_use, "", 11)
            pdf.multi_cell(0, 6, ozet)

        # ÇIKTI ALMA (BOŞ SAYFA SORUNUNU ÇÖZEN KISIM)
        try:
            # bytearray kullanarak doğrudan bellekten çıktı alıyoruz
            pdf_output = pdf.output()
            
            # fpdf2'de output() direkt bytes döndürür
            st.download_button(
                label="✅ ŞİMDİ BURADAN İNDİR",
                data=pdf_output,
                file_name="CV_Faruk.pdf",
                mime="application/pdf"
            )
            st.success("İşlem tamam! Yukarıdaki butona basarak indirebilirsin.")
        except Exception as e:
            st.error(f"Hata: {e}")