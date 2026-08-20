# ☁️ دستیار هوشمند و عامل خودمختار مستندات ابری لیارا (Liara Agentic RAG Assistant)

پروژه دستیار هوشمند، عامل خودمختار و موتور جستجوی هیبریدی پایگاه دانش پلتفرم ابری **لیارا (Liara Cloud)**، توسعه‌یافته بر پایه ۲,۲۸۷ سند رسمی، راهنماهای استقرار، رفع خطاهای متداول و تولید خودکار فایل‌های پیکربندی.

---

## 🌟 ویژگی‌های برجسته پلتفرم

1. **موتور جستجوی هیبریدی (Hybrid RAG: BM25 + Reciprocal Rank Fusion):**
   - تحلیل و چانک‌بندی عمیق مستندات رسمی تمام پلتفرم‌ها (NodeJS، Laravel، Django، Next.js، Docker، PostgreSQL، MySQL، Redis، Storage، DNS و ...).
   - سرعت پاسخ‌دهی آنی (زیر ۱۵ میلی‌ثانیه) با سیستم کشینگ معنایی (Semantic In-Memory Cache).
2. **استناد دقیق به منابع (100% Direct Official Citations):**
   - هر پاسخ حاوی لینک‌های مستقیم و تفکیک‌شده به صفحات مستندات رسمی وب‌سایت `https://docs.liara.ir` است.
3. **ابزارهای عامل هوشمند (Agentic Tooling & Diagnostics):**
   - تولید خودکار و استاندارد فایل پیکربندی `liara.json` متناسب با پشته فنی کاربر.
   - موتور هوشمند عیب‌یابی خطای ۵۰۲ (Bad Gateway)، مشکلات Port Binding، سیستم فایل Read-Only و رفع خطاهای استقرار.
4. **رابط کاربری لوکس سرخ‌آب (Sorkhab Enterprise UI/UX):**
   - دارای دو تم کامل تاریک (Dark Mode) و روشن (Light Mode) با پالت استاندارد سرخ‌آب (`#00baba` و `#06090e`).
   - فونت استاندارد یکان‌بخ (Yekan Bakh FaNum)، قابلیت کپی یک‌کلیکه کدها و هایلایت سینتکس ترمینال.
5. **آماده استقرار ابری (Cloud-Native & Docker Ready):**
   - دارای مانیفست‌های کامل `liara.json` و `Dockerfile` چندمرحله‌ای بهینه برای استقرار مستقیم روی PaaS لیارا.

---

## 🛠️ ساختار ماژولار پروژه

```
liara-assistant/
├── server.py              # موتور پردازش RAG، روت‌های API و سیستم کشینگ (FastAPI)
├── build_index.py         # اسکریپت استخراج، پارس و ایندکس مستندات MDX
├── knowledge_base.json    # پایگاه دانش ساختاریافته شامل ۱,۱۴۲ مقاله و ۴,۰۰۰+ چانک
├── templates/
│   └── index.html         # رابط کاربری وب چت با تم دوگانه و هایلایت کد
├── public/                # استت‌های استاتیک و آیکون‌ها
├── requirements.txt       # نیازمندی‌های پایتون
├── Dockerfile             # کانتینر داکر استاندارد
└── liara.json             # مانیفست استقرار در پلتفرم لیارا
```

---

## 🚀 راه‌اندازی و استقرار محلی (Local Setup)

```bash
# ۱. نصب پیش‌نیازها
pip install -r requirements.txt

# ۲. اجرای سرور
python server.py
```

سپس در مرورگر به آدرس `http://localhost:3025` مراجعه فرمایید.

---

## 🌐 لینک‌های نسخه لایو

- 🔗 **نسخه لایو سرور حسام:** [https://liara.shop4bit.ir](https://liara.shop4bit.ir)
- 📖 **مستندات رسمی لیارا:** [https://docs.liara.ir](https://docs.liara.ir)
