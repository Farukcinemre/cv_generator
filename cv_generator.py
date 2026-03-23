import streamlit as st
from fpdf import FPDF
import json
import os
from PIL import Image

# --- PDF SINIFI GÜNCELLEME ---
class PDF(FPDF):
    def __init__(self, theme_color=(0, 0, 0)):
        # fpdf2 kullanıyorsak unit="mm" eklemek iyidir
        super().__init__()
        self.theme_color = theme_color
        
        # Font yolları
        f_reg = "arial.ttf"
        f_bold = "arialbd.ttf"

        if os.path.exists(f_reg):
            # ÖNEMLİ: uni=True parametresi eski fpdf sürümlerinde Unicode'u açar
            self.add_font("ArialTR", "", f_reg, uni=True) 
            if os.path.exists(f_bold):
                self.add_font("ArialTR", "B", f_bold, uni=True)
            self.font_family_to_use = "ArialTR"
        else:
            self.font_family_to_use = "Arial" # Helvetica yerine Arial (Unicode destekli sistemlerde)

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

if "cv_data" not in st.session_state:
    st.session_state["cv_data"] = {}

st.sidebar.header("💾 Taslak Yönetimi")
uploaded_file = st.sidebar.file_uploader("Önceki Taslağı (.json) Yükle", type="json")

# HATA DÜZELTME: JSON okuma sırasında Unicode hatasını engellemek için decode ekledik
if uploaded_file:
    try:
        # Dosyayı byte olarak okuyup utf-8 formatına zorluyoruz
        file_bytes = uploaded_file.read()
        st.session_state["cv_data"] = json.loads(file_bytes.decode("utf-8"))
    except Exception as e:
        st.error(f"Taslak yüklenirken bir hata oluştu: {e}")

d = st.session_state["cv_data"]

st.sidebar.header("🎨 Görünüm Ayarları")
tema_rengi = st.sidebar.color_picker("Tema Rengi", d.get("tema_rengi", "#003366"))
hex_color = tema_rengi.lstrip('#')
rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
satir_araligi = st.sidebar.slider("Satır Boşluğu", 4, 10, d.get("satir_araligi", 6))

st.title("🚀 Profesyonel CV Oluşturucu")

col_main, col_preview = st.columns([2, 1])

with col_main:
    # 1. KİŞİSEL BİLGİLER
    with st.expander("👤 Kişisel Bilgiler & Fotoğraf", expanded=True):
        f_col1, f_col2 = st.columns([1, 3])
        with f_col1:
            uploaded_photo = st.file_uploader("Vesikalık", type=["jpg", "png", "jpeg"])
            if uploaded_photo: st.image(uploaded_photo, width=120)
        with f_col2:
            isim = st.text_input("Ad Soyad", d.get("isim", ""))
            email = st.text_input("E-posta", d.get("email", ""))
        c1, c2 = st.columns(2)
        telefon = c1.text_input("Telefon", d.get("telefon", "+90"))
        lokasyon = c2.text_input("Şehir/Ülke", d.get("lokasyon", ""))
        l1, l2, l3 = st.columns(3)
        linkedin = l1.text_input("LinkedIn", d.get("linkedin", ""))
        github = l2.text_input("GitHub", d.get("github", ""))
        portfolio = l3.text_input("Portfolyo", d.get("portfolio", ""))

    # 2. ÖZET
    with st.expander("📝 Profesyonel Özet"):
        ozet = st.text_area("Kısa Tanıtım", d.get("ozet", ""))

    # 3. İŞ DENEYİMİ
    with st.expander("💼 İş Deneyimi"):
        d_sayi = st.number_input("Deneyim Sayısı", 1, 10, max(1, len(d.get("deneyimler", [0]))))
        deneyimler = []
        for i in range(d_sayi):
            prev_d = d.get("deneyimler", [{}])[i] if i < len(d.get("deneyimler", [])) else {}
            cc1, cc2 = st.columns([2, 1])
            u = cc1.text_input(f"Ünvan {i}", prev_d.get("u", ""), key=f"u_{i}")
            s = cc1.text_input(f"Şirket {i}", prev_d.get("s", ""), key=f"s_{i}")
            t = cc2.text_input(f"Tarih {i}", prev_d.get("t", ""), key=f"t_{i}")
            detay = st.text_area(f"Detaylar {i}", "\n".join(prev_d.get("d", []) if isinstance(prev_d.get("d"), list) else ""), key=f"d_{i}")
            deneyimler.append({"u": u, "s": s, "t": t, "d": detay.split('\n')})

    # 4. PROJELER
    with st.expander("💻 Projeler"):
        p_sayi = st.number_input("Proje Sayısı", 0, 10, len(d.get("projeler", [])))
        projeler = []
        for i in range(p_sayi):
            prev_p = d.get("projeler", [{}])[i] if i < len(d.get("projeler", [])) else {}
            pn = st.text_input(f"Proje Adı {i}", prev_p.get("n", ""), key=f"pn_{i}")
            pt = st.text_input(f"Teknolojiler {i}", prev_p.get("t", ""), key=f"pt_{i}")
            pd = st.text_area(f"Açıklama {i}", prev_p.get("d", ""), key=f"pd_{i}")
            projeler.append({"n": pn, "t": pt, "d": pd})

    # 5. EĞİTİM
    with st.expander("🎓 Eğitim Bilgileri"):
        e_sayi = st.number_input("Eğitim Sayısı", 1, 5, max(1, len(d.get("egitim_listesi", [0]))))
        egitim_listesi = []
        for i in range(e_sayi):
            prev_e = d.get("egitim_listesi", [{}])[i] if i < len(d.get("egitim_listesi", [])) else {}
            ec1, ec2 = st.columns([2, 1])
            okul = ec1.text_input(f"Okul Adı {i}", prev_e.get("okul", ""), key=f"okul_{i}")
            bolum = ec1.text_input(f"Bölüm {i}", prev_e.get("bolum", ""), key=f"bolum_{i}")
            e_tarih = ec2.text_input(f"Mezuniyet Tarihi {i}", prev_e.get("tarih", ""), key=f"et_{i}")
            e_gpa = ec2.text_input(f"GPA {i}", prev_e.get("gpa", ""), key=f"egpa_{i}")
            egitim_listesi.append({"okul": okul, "bolum": bolum, "tarih": e_tarih, "gpa": e_gpa})

    # 6. DİLLER
    with st.expander("🌐 Yabancı Diller"):
        dil_sayi = st.number_input("Dil Sayısı", 0, 5, len(d.get("dil_listesi", [])))
        dil_listesi = []
        for i in range(dil_sayi):
            prev_l = d.get("dil_listesi", [{}])[i] if i < len(d.get("dil_listesi", [])) else {}
            lc1, lc2 = st.columns(2)
            dil_ad = lc1.text_input(f"Dil {i}", prev_l.get("ad", ""), key=f"dil_ad_{i}")
            options = ["Başlangıç", "Orta", "İleri", "Anadil", "A1", "A2", "B1", "B2", "C1", "C2"]
            current_seviye = prev_l.get("seviye", "Başlangıç")
            try:
                idx = options.index(current_seviye)
            except ValueError:
                idx = 0
            dil_seviye = lc2.selectbox(f"Seviye {i}", options, index=idx, key=f"dil_s_{i}")
            dil_listesi.append({"ad": dil_ad, "seviye": dil_seviye})

    # 7. REFERANSLAR
    with st.expander("📞 Referanslar"):
        ref_sayi = st.number_input("Referans Sayısı", 0, 5, len(d.get("referans_listesi", [])))
        referans_listesi = []
        for i in range(ref_sayi):
            prev_r = d.get("referans_listesi", [{}])[i] if i < len(d.get("referans_listesi", [])) else {}
            rc1, rc2 = st.columns(2)
            ref_ad = rc1.text_input(f"Referans Ad Soyad {i}", prev_r.get("ad", ""), key=f"ref_ad_{i}")
            ref_unvan = rc2.text_input(f"Unvan / Şirket {i}", prev_r.get("unvan", ""), key=f"ref_u_{i}")
            ref_iletisim = st.text_input(f"İletişim Bilgisi {i}", prev_r.get("iletisim", ""), key=f"ref_i_{i}")
            referans_listesi.append({"ad": ref_ad, "unvan": ref_unvan, "iletisim": ref_iletisim})

    # 8. YETENEKLER
    with st.expander("🛠 Yetenekler"):
        yetenekler = st.text_area("Yetenekler", d.get("yetenekler", ""))

# Taslak Kaydetme
current_data = {
    "isim": isim, "email": email, "telefon": telefon, "lokasyon": lokasyon,
    "linkedin": linkedin, "github": github, "portfolio": portfolio,
    "ozet": ozet, "deneyimler": deneyimler, "projeler": projeler,
    "egitim_listesi": egitim_listesi, "dil_listesi": dil_listesi, 
    "referans_listesi": referans_listesi, "yetenekler": yetenekler, 
    "tema_rengi": tema_rengi, "satir_araligi": satir_araligi
}
# JSON kaydederken utf-8 zorlaması yaptık
st.sidebar.download_button("📥 Taslağı Kaydet", data=json.dumps(current_data, ensure_ascii=False), file_name="cv_taslak.json")

# --- PDF OLUŞTURMA ---
if st.button("✨ CV'Yİ PDF OLARAK OLUŞTUR"):
    if not isim:
        st.error("Lütfen en azından 'Ad Soyad' kısmını doldurun.")
    else:
        pdf = PDF(theme_color=rgb_color)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Header & Fotoğraf
        if uploaded_photo:
            with open("temp_p.png", "wb") as f: f.write(uploaded_photo.getbuffer())
            pdf.image("temp_p.png", x=165, y=10, w=35, h=45)
            header_width = 150
        else:
            header_width = 190

        pdf.set_font(pdf.font_family_to_use, "B", 24)
        pdf.set_text_color(*rgb_color)
        pdf.cell(header_width, 12, isim, ln=True)
        
        pdf.set_font(pdf.font_family_to_use, "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(header_width, 5, f"{lokasyon} | {telefon} | {email}", ln=True)
        
        pdf.set_font(pdf.font_family_to_use, "I", 9)
        pdf.set_text_color(*rgb_color)
        for link in [linkedin, github, portfolio]:
            if link and link.strip(): pdf.cell(header_width, 5, link.strip(), ln=True)
        
        if pdf.get_y() < 60: pdf.set_y(60)

        # Bölümler
        if ozet:
            pdf.draw_section_header("Profil")
            pdf.set_font(pdf.font_family_to_use, "", 11)
            pdf.multi_cell(0, satir_araligi, ozet)

        if deneyimler:
            pdf.draw_section_header("İş Deneyimi")
            for dn in deneyimler:
                if dn.get('u'):
                    pdf.set_font(pdf.font_family_to_use, "B", 11)
                    pdf.cell(140, 7, f"{dn['u']} - {dn['s']}")
                    pdf.set_font(pdf.font_family_to_use, "I", 10)
                    pdf.cell(0, 7, dn['t'], ln=True, align="R")
                    pdf.set_font(pdf.font_family_to_use, "", 10)
                    for m in dn.get('d', []):
                        if m.strip(): pdf.multi_cell(0, satir_araligi - 1, f"  - {m.strip()}")
                    pdf.ln(1)

        if projeler:
            pdf.draw_section_header("Projeler")
            for pr in projeler:
                if pr.get('n'):
                    pdf.set_font(pdf.font_family_to_use, "B", 11)
                    pdf.cell(0, 7, f"{pr['n']} ({pr.get('t', '')})", ln=True)
                    pdf.set_font(pdf.font_family_to_use, "", 10)
                    pdf.multi_cell(0, satir_araligi - 1, f"  • {pr.get('d', '')}")
                    pdf.ln(1)

        if egitim_listesi:
            pdf.draw_section_header("Eğitim")
            for edu in egitim_listesi:
                if edu.get('okul'):
                    pdf.set_font(pdf.font_family_to_use, "B", 11)
                    pdf.cell(140, 7, edu['okul'])
                    pdf.set_font(pdf.font_family_to_use, "I", 10)
                    pdf.cell(0, 7, edu.get('tarih', ''), ln=True, align="R")
                    pdf.set_font(pdf.font_family_to_use, "", 10)
                    pdf.cell(0, 6, edu.get('bolum', ''), ln=True)
                    if edu.get('gpa'):
                        pdf.set_font(pdf.font_family_to_use, "B", 10)
                        pdf.cell(0, 6, f"GPA: {edu['gpa']}", ln=True)
                    pdf.ln(2)

        if dil_listesi:
            pdf.draw_section_header("Diller")
            for dil in dil_listesi:
                if dil.get('ad'):
                    pdf.set_font(pdf.font_family_to_use, "B", 10)
                    pdf.cell(40, 6, f"{dil['ad']}:")
                    pdf.set_font(pdf.font_family_to_use, "", 10)
                    pdf.cell(0, 6, dil['seviye'], ln=True)

        if referans_listesi:
            pdf.draw_section_header("Referanslar")
            for ref in referans_listesi:
                if ref.get('ad'):
                    pdf.set_font(pdf.font_family_to_use, "B", 11)
                    pdf.cell(0, 6, ref['ad'], ln=True)
                    pdf.set_font(pdf.font_family_to_use, "", 10)
                    pdf.cell(0, 5, ref.get('unvan', ''), ln=True)
                    pdf.set_font(pdf.font_family_to_use, "I", 9)
                    pdf.cell(0, 5, ref.get('iletisim', ''), ln=True)
                    pdf.ln(2)

        if yetenekler:
            pdf.draw_section_header("Yetenekler")
            pdf.set_font(pdf.font_family_to_use, "", 9)
            pdf.multi_cell(0, 4, yetenekler)

        # PDF Çıktısı
        pdf_bytes = pdf.output(dest='S')
        st.sidebar.download_button("✅ PDF'İ İNDİR", data=pdf_bytes, file_name=f"{isim}_CV.pdf", mime="application/pdf")
        st.success("CV Hazır! Sol taraftaki butondan indirebilirsin.")