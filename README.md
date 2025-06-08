# 🧾 Ovqatlanish_DB — Umumiy Ovqatlanish Tarmog'ini Monitoring Qilish Ilovasi

## 📌 Tavsif
Ushbu loyiha umumiy ovqatlanish tarmog‘i faoliyatini monitoring qilish uchun mo‘ljallangan veb-ilovadir. Tizim restoran va filiallar ishini nazorat qilish, buyurtmalarni boshqarish, xodimlar samaradorligini tahlil qilish, moliyaviy va mahsulot omborini monitoring qilish imkonini beradi.

## ⚙️ Texnologiyalar
- 🐍 Django (Python backend)
- 🗃️ PostgreSQL (ma'lumotlar bazasi)
- 💻 HTML, CSS, JavaScript (frontend)
- 📊 Pandas, Scikit-learn, Matplotlib (tahliliy va AI komponentlari)

## 🚀 Asosiy funksiyalar
- 🍽️ Restoran va filiallar faoliyatini kuzatish
- 📦 Ombor zaxiralarini boshqarish
- 🧾 Buyurtmalar va mijozlar statistikasi
- 👨‍🍳 Xodimlar ish faoliyatini nazorat qilish
- 📈 Moliyaviy hisob-kitob va tahlillar
- 🤖 AI yordamida:
  - Buyurtmalarni bashorat qilish
  - Mijozlarga menyu tavsiyalari
  - Xodim samaradorligini baholash
  - Zaxiralarni optimallashtirish

## 🖥️ Ilovani ishga tushirish
```bash
# 1. Loyihani klonlash
git clone https://github.com/Habibullo2003/ovqatlanish_db.git
cd ovqatlanish_db

# 2. Virtual muhit yaratish
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# 3. Kerakli kutubxonalarni o‘rnatish
pip install -r requirements.txt

# 4. Migratsiyalarni bajarish
python manage.py makemigrations
python manage.py migrate

# 5. Admin foydalanuvchi yaratish
python manage.py createsuperuser

# 6. Serverni ishga tushirish
python manage.py runserver
