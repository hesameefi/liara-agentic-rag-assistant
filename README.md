# ☁️ دستیار هوشمند و عامل خودمختار مستندات ابری لیارا
# Liara Cloud Agentic RAG Documentation Assistant

<div align="center">

[![Live Demo](https://img.shields.io/badge/Live_Demo-https%3A%2F%2Fliara.shop4bit.ir-00baba?style=for-the-badge&logo=google-chrome&logoColor=white)](https://liara.shop4bit.ir)
[![Official Docs](https://img.shields.io/badge/Liara_Docs-https%3A%2F%2Fdocs.liara.ir-087373?style=for-the-badge&logo=bookstack&logoColor=white)](https://docs.liara.ir)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

**دستیار هوشمند فنی، عامل خودمختار تولید پیکربندی ابری و موتور عیب‌یابی پلتفرم ابری لیارا**
*An intelligent technical documentation assistant, autonomous cloud deployment generator, and diagnostics engine for Liara Cloud.*

[فارسی](#-معرفی-پروژه-به-زبان-فارسی) • [English](#-english-documentation)

---

</div>

## 🇮🇷 معرفی پروژه (به زبان فارسی)

این پروژه یک **عامل هوشمند (Agentic RAG Assistant)** است که بر پایه **۱,۱۴۲ مقاله و بیش از ۴,۰۰۰ چانک رسمی از مستندات پلتفرم ابری لیارا (Liara Cloud)** طراحی و پیاده‌سازی شده است. این سامانه توسعه‌دهندگان را در استقرار برنامه‌ها، اتصال پایگاه‌های داده، رفع خطاهای رایج مانند ۵۰۲ و تولید خودکار فایل‌های پیکربندی `liara.json` راهنمایی می‌کند.

### 🌟 ویژگی‌های کلیدی:
1. **موتور جستجوی ترکیبی (Hybrid RAG: BM25 + Reciprocal Rank Fusion):**
   - ترکیب جستجوی کلیدواژه‌ای دقیق (برای دستورات CLI، پورت‌ها، متغیرها) و جستجوی مفهومی.
   - بازیابی و پاسخ‌دهی فوق سریع (زیر ۱۵ میلی‌ثانیه).
2. **استناد ۱۰۰٪ دقیق به منابع رسمی (Official Citations):**
   - ارائه لینک‌های مستقیم و تفکیک‌شده به صفحات مرتبط در وب‌سایت `https://docs.liara.ir`.
3. **تولید خودکار فایل پیکربندی (`liara.json` Generator):**
   - ساخت کانفیگ متناسب با هر پلتفرم (NodeJS, Laravel, Django, Next.js, Docker, Python, Go و ...).
4. **موتور عیب‌یابی هوشمند (Automated Troubleshooting):**
   - تحلیل خطاهای ۵۰۲ Bad Gateway، مشکلات دیسک دائمی (Persistent Disk) و کانفیگ پورت‌ها.
5. **رابط کاربری مدرن سرخ‌آب (Sorkhab Enterprise UI/UX):**
   - پشتیبانی از هر دو تم تاریک و روشن (Dark & Light Mode).
   - تایپوگرافی رسمی یکان‌بخ (Yekan Bakh FaNum).
   - دکمه کپی ۱-کلیکه دستورات و هایلایت رنگی سینتکس کدها.

---

## 🇬🇧 English Documentation

**Liara Agentic RAG Assistant** is an autonomous AI assistant powered by a hybrid retrieval engine indexed over **1,142 official documentation pages and 4,000+ chunks** from Liara Cloud. It assists software developers in deploying applications, managing databases, diagnosing container errors, and automatically generating deployment manifests.

### 🚀 Key Features:
- **Hybrid Retrieval-Augmented Generation (Hybrid RAG):** Combines BM25 lexical token matching for exact technical keywords (`liara.json`, ports, CLI flags) with contextual semantics.
- **Direct Official Citations:** Every single answer is strictly grounded in official Liara docs with direct clickable citation URLs.
- **Automated `liara.json` Generator:** Produces valid deployment configuration files for any stack.
- **Smart Error Diagnostics:** Instant root-cause analysis and step-by-step resolution for 502 Bad Gateway, Read-Only file systems, and port mismatches.
- **High-End Sorkhab Design:** Responsive dual-theme interface (Dark/Light), code syntax highlighting with 1-click copying.
- **Cloud Native & Ultra-Fast:** Sub-15ms latency with async FastAPI engine and in-memory semantic caching.

---

## 🛠️ ساختار ماژولار پروژه (Architecture)

```
liara-agentic-rag-assistant/
├── server.py              # موتور اصلی RAG، کنترلرهای API و سیستم کشینگ
├── build_index.py         # اسکریپت استخراج، پارس و ایندکس مستندات MDX
├── knowledge_base.json    # پایگاه دانش ساختاریافته شامل ۱,۱۴۲ مقاله رسمی
├── templates/
│   └── index.html         # رابط کاربری وب چت با تم دوگانه
├── public/
│   └── favicon.svg        # فاوآیکون اختصاصی
├── requirements.txt       # نیازمندی‌های پایتون (FastAPI, Uvicorn, Requests)
├── Dockerfile             # مانیفست کانتینرسازی داکر
└── liara.json             # مانیفست استقرار ابری در لیارا
```

---

## 💻 راه‌اندازی و اجرای محلی (Local Quickstart)

```bash
# ۱. کلون ریپازیتوری
git clone https://github.com/hesameefi/liara-agentic-rag-assistant.git
cd liara-agentic-rag-assistant

# ۲. نصب نیازمندی‌ها
pip install -r requirements.txt

# ۳. اجرای سرور
python server.py
```

سپس در مرورگر خود آدرس `http://localhost:3025` را باز نمایید.

---

## 🌐 لینک‌های دسترسی (Live Access Links)

- 🔗 **نسخه آنلاین پروژه (Live Production):** [https://liara.shop4bit.ir](https://liara.shop4bit.ir)
- 📖 **مستندات رسمی پلتفرم ابری لیارا:** [https://docs.liara.ir](https://docs.liara.ir)

---

## 📄 مجوز (License)
این پروژه تحت مجوز **MIT** منتشر شده است.
