# Python 3.11'in 'slim' versiyonu yerine daha kapsamlı olan 'buster' veya 'bookworm' kullanabilirsin
# Eğer 'slim' kullanacaksan sadece gerekli olanları ekleyelim
FROM python:3.11-slim

WORKDIR /app

# Sadece font desteği ve temel araçlar için gerekli minimum paketler
# Hatayı önlemek için 'fix-missing' ekledik
RUN apt-get update --fix-missing && apt-get install -y \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Dosyaları kopyala
COPY . .

# Kütüphaneleri kur
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Streamlit'in Docker içinde düzgün çalışması için flaglar eklendi
ENTRYPOINT ["streamlit", "run", "cv_generator.py", "--server.port=8501", "--server.address=0.0.0.0"]