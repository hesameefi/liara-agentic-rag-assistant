import os
import re
import json
import time
import math
import asyncio
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests

app = FastAPI(title="Liara Cloud AI Documentation Assistant", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "knowledge_base.json")
STATIC_DIR = os.path.join(BASE_DIR, "public")
os.makedirs(STATIC_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Inverted Index & BM25 Retrieval Engine
# ---------------------------------------------------------------------------
class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: List[Dict[str, Any]] = []
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lens: List[int] = []
        self.doc_freqs: Dict[str, int] = defaultdict(int)
        self.inverted_index: Dict[str, List[tuple]] = defaultdict(list)
        self.platforms = set()

    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        # Preserve technical tokens like liara.json, package.json, --app, etc.
        tokens = re.findall(r'[a-z0-9_\-\.\:\/]+|[\u0600-\u06FF]+', text)
        return [t for t in tokens if len(t) > 1 or re.match(r'[\u0600-\u06FF]', t)]

    def load_knowledge_base(self, filepath: str):
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found.")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_docs = json.load(f)

        # Flatten sections into searchable chunks
        chunks = []
        for d in raw_docs:
            p = d.get('platform', 'general')
            c = d.get('category', 'general')
            self.platforms.add(p)
            for sec in d.get('sections', []):
                chunk_text = f"{d['title']} {sec['section_title']} {sec['text']}"
                chunks.append({
                    "doc_title": d['title'],
                    "section_title": sec['section_title'],
                    "platform": p,
                    "category": c,
                    "url": d['url'],
                    "text": sec['text'],
                    "codes": sec.get('codes', [])
                })

        self.docs = chunks
        self.corpus_size = len(chunks)
        total_len = 0

        for idx, doc in enumerate(chunks):
            text_to_index = f"{doc['doc_title']} {doc['section_title']} {doc['platform']} {doc['category']} {doc['text']}"
            tokens = self.tokenize(text_to_index)
            doc_len = len(tokens)
            self.doc_lens.append(doc_len)
            total_len += doc_len

            counts = Counter(tokens)
            for term, count in counts.items():
                self.doc_freqs[term] += 1
                self.inverted_index[term].append((idx, count))

        self.avg_doc_len = (total_len / self.corpus_size) if self.corpus_size > 0 else 1.0
        print(f"BM25 Index ready with {self.corpus_size} chunks across {len(self.platforms)} platforms.")

    def search(self, query: str, platform_filter: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        tokens = self.tokenize(query)
        if not tokens or self.corpus_size == 0:
            return []

        scores = defaultdict(float)
        
        # Platform detection in query
        detected_platform = None
        for p in self.platforms:
            if p in query.lower() and len(p) > 2:
                detected_platform = p
                break
        
        filter_p = platform_filter or detected_platform

        for term in tokens:
            if term not in self.doc_freqs:
                continue
            df = self.doc_freqs[term]
            idf = math.log(1 + (self.corpus_size - df + 0.5) / (df + 0.5))

            for doc_idx, tf in self.inverted_index[term]:
                doc_len = self.doc_lens[doc_idx]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                score = idf * (numerator / denominator)

                # Boost if platform matches
                doc = self.docs[doc_idx]
                if filter_p and (doc['platform'] == filter_p or doc['category'] == filter_p):
                    score *= 1.8
                
                # Boost if term in doc title
                if term in doc['doc_title'].lower():
                    score *= 1.5

                scores[doc_idx] += score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_idx, score in ranked:
            doc = self.docs[doc_idx]
            results.append({
                "title": doc['doc_title'],
                "section": doc['section_title'],
                "platform": doc['platform'],
                "category": doc['category'],
                "url": doc['url'],
                "text": doc['text'],
                "codes": doc['codes'],
                "score": round(score, 3)
            })
        return results

retriever = BM25Retriever()

# ---------------------------------------------------------------------------
# Agentic Tools & Configuration Generator
# ---------------------------------------------------------------------------
def generate_liara_json(platform: str, port: int = 3000, disk_name: str = "", mount_path: str = "", app_name: str = "my-app") -> Dict[str, Any]:
    config = {
        "app": app_name,
        "platform": platform
    }
    if port:
        config["port"] = port
    
    if platform == "laravel":
        config["laravel"] = {
            "webserver": "nginx"
        }
    elif platform == "django":
        config["django"] = {
            "timezone": "Asia/Tehran"
        }
    elif platform == "node":
        config["node"] = {
            "version": "20"
        }
    elif platform == "python":
        config["python"] = {
            "version": "3.11"
        }

    if disk_name and mount_path:
        config["disks"] = [
            {
                "name": disk_name,
                "mountTo": mount_path
            }
        ]
    return config

def diagnose_liara_error(error_log: str) -> Dict[str, str]:
    log_lower = error_log.lower()
    if "502" in log_lower or "bad gateway" in log_lower:
        return {
            "issue": "خطای 502 Bad Gateway در وب‌سرور Nginx لیارا",
            "root_cause": "پورت برنامه با پورت تعریف‌شده در کنسول لیارا یا فایل liara.json همخوانی ندارد یا وب‌سرور داخلی برنامه هنوز Listen نکرده است.",
            "solution": "1. مطمئن شوید برنامه روی پورت 0.0.0.0 (نه فقط 127.0.0.1) اجرا می‌شود.\n2. مقدار `port` را در فایل `liara.json` دقیقاً برابر پورتی بگذارید که برنامه روی آن بالا می‌آید (مثلاً 3000 یا 8080).\n3. در نودجی‌اس از `process.env.PORT || 3000` استفاده نمایید.",
            "doc_url": "https://docs.liara.ir/paas/details/logs/"
        }
    elif "readonly" in log_lower or "read-only file system" in log_lower or "sqlite" in log_lower:
        return {
            "issue": "سیستم فایل فقط-خواندنی (Read-Only File System) یا پاک شدن دیتابیس SQLite",
            "root_cause": "فایل سیستم برنامه‌ها در سرویس ابری لیارا به صورت Stateless (ناپایدار) است و برای ذخیره دائمی فایل‌ها نیاز به دیسک ابری (Persistent Disk) دارید.",
            "solution": "1. در منوی دیسک‌ها یک دیسک بسازید (مثلاً data).\n2. دیسک را در فایل `liara.json` به پوشه دیتابیس یا آپلودها متصل (Mount) کنید:\n```json\n{\n  \"disks\": [{\n    \"name\": \"data\",\n    \"mountTo\": \"/app/storage\"\n  }]\n}\n```",
            "doc_url": "https://docs.liara.ir/paas/disks/create/"
        }
    elif "procfile" in log_lower or "start script missing" in log_lower:
        return {
            "issue": "نبود اسکریپت اجرای اولیه (Start Script / Procfile)",
            "root_cause": "لیارا نمی‌داند برنامه را با چه دستوری استارت کند.",
            "solution": "1. در پروژه یک فایل بدون پسوند به نام `Procfile` بسازید و دستور استارت را بنویسید (مثلاً `web: gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT` یا `web: npm start`).\n2. در پکیج جی‌سان مطمئن شوید اسکریپت `\"start\"` تعریف شده است.",
            "doc_url": "https://docs.liara.ir/paas/nodejs/how-tos/use-procfile/"
        }
    else:
        return {
            "issue": "بررسی لاگ اجرای استقرار",
            "root_cause": "خطا در فرآیند Build یا اجرای کانتینر پروژه.",
            "solution": "دستور `liara logs` را در ترمینال اجرا کنید تا جزییات خطا را لحظه‌ای مشاهده نمایید.",
            "doc_url": "https://docs.liara.ir/paas/details/logs/"
        }

# ---------------------------------------------------------------------------
# Semantic In-Memory Response Cache
# ---------------------------------------------------------------------------
RESPONSE_CACHE: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Core Agent Query Processor
# ---------------------------------------------------------------------------
async def process_agent_chat(query: str, platform_filter: Optional[str] = None) -> Dict[str, Any]:
    cache_key = f"{query.strip().lower()}_{platform_filter or ''}"
    if cache_key in RESPONSE_CACHE:
        return RESPONSE_CACHE[cache_key]

    # 1. Intent Detection
    intent = "general_search"
    if "liara.json" in query.lower() or "کانفیگ" in query or "پورت" in query:
        intent = "generate_config"
    elif "502" in query or "ارور" in query or "خطا" in query or "crash" in query or "error" in query.lower():
        intent = "troubleshoot"

    # 2. Retrieve Top Chunks via BM25
    results = retriever.search(query, platform_filter=platform_filter, top_k=4)

    # 3. Formulate Rich Answer
    citations = []
    seen_urls = set()
    for r in results:
        if r['url'] not in seen_urls:
            citations.append({
                "title": r['title'],
                "section": r['section'],
                "url": r['url'],
                "platform": r['platform']
            })
            seen_urls.add(r['url'])

    # Build Context
    context_text = "\n\n".join([f"### [{r['title']} - {r['section']}]({r['url']})\n{r['text']}" for r in results])

    # Dynamic suggestions based on query
    suggestions = [
        "چطور دیسک ابری (Disk) بسازم و وصل کنم؟",
        "نحوه استقرار خودکار با GitHub Actions",
        "رفع خطای 502 Bad Gateway در لیارا"
    ]
    if "laravel" in query.lower() or "لاراول" in query:
        suggestions = [
            "اتصال دیتابیس MySQL به لاراول در لیارا",
            "اجرای دستورات php artisan migrate و Seeder",
            "نحوه فعال‌سازی صف‌ها (Queues) و ورکرها در لاراول"
        ]
    elif "django" in query.lower() or "جنگو" in query:
        suggestions = [
            "تنظیمات Static Files و WhiteNoise در جنگو",
            "اتصال پایگاه داده PostgreSQL به جنگو",
            "فایل Procfile استاندارد برای اجرای Gunicorn"
        ]
    elif "node" in query.lower() or "next" in query.lower() or "نود" in query:
        suggestions = [
            "تنظیم پورت متغیر PORT در Express و Fastify",
            "نحوه استقرار Next.js با خروجی Standalone",
            "مدیریت متغیرهای محیطی (.env) در نودجی‌اس"
        ]
    elif "docker" in query.lower() or "داکر" in query:
        suggestions = [
            "نمونه Dockerfile چندمرحله‌ای بهینه برای لیارا",
            "استفاده از دیسک دائمی در کانتینر داکر",
            "تنظیم Entrypoint و پورت ورودی در داکر"
        ]

    # Structured Response Construction
    formatted_reply = ""
    
    # 1. Troubleshoot Intent
    if intent == "troubleshoot" and ("502" in query or "bad gateway" in query.lower()):
        diag = diagnose_liara_error(query)
        formatted_reply = f"""### ⚠️ عیب‌یابی: {diag['issue']}

**علت اصلی خطا:**
{diag['root_cause']}

---

### 🛠️ راه‌حل گام‌به‌گام:
{diag['solution']}

---

### 📄 نمونه فایل `liara.json` استاندارد برای رفع مشکل پورت:
```json
{{
  "platform": "node",
  "port": 3000
}}
```

> [!TIP]
> برای مشاهده لاگ‌های زنده در لحظه بالا آمدن کانتینر، از دستور زیر در خط فرمان استفاده کنید:
> ```bash
> liara logs --follow
> ```
"""
    # 2. Config Generator Intent
    elif intent == "generate_config":
        plat = platform_filter or ("laravel" if "laravel" in query.lower() else "node" if "node" in query.lower() else "django" if "django" in query.lower() else "docker" if "docker" in query.lower() else "python")
        cfg = generate_liara_json(plat, port=3000, disk_name="storage_disk", mount_path="/app/storage", app_name="my-app")
        cfg_str = json.dumps(cfg, indent=2, ensure_ascii=False)
        formatted_reply = f"""### ⚙️ فایل پیکربندی استاندارد `liara.json` برای پلتفرم **{plat.upper()}**:

فایل زیر را در ریشه اصلی (Root) پروژه خود ایجاد نمایید:

```json
{cfg_str}
```

---

### 🚀 نحوه استقرار در خط فرمان (Liara CLI):
```bash
# ۱. ورود به حساب کاربری لیارا
liara login

# ۲. استقرار سریع با استفاده از تنظیمات liara.json
liara deploy
```

> [!NOTE]
> برای افزودن دیسک دائمی یا متغیرهای محیطی اختصاصی، می‌توانید فیلدهای `disks` و `env` را در همین فایل ویرایش کنید.
"""
    # 3. Topic: Laravel & MySQL / Databases
    elif ("laravel" in query.lower() or "لاراول" in query) and ("mysql" in query.lower() or "دیتابیس" in query or "پایگاه داده" in query):
        formatted_reply = """### 🐘 راهنمای اتصال دیتابیس MySQL به لاراول (Laravel) در لیارا

برای اتصال پایگاه داده مدیریت‌شده MySQL به برنامه لاراول، مراحل زیر را به ترتیب انجام دهید:

---

### ۱. تنظیم متغیرهای محیطی (`.env`)
در داشبورد لیارا، وارد بخش **متغیرها (Environment Variables)** برنامه لاراول خود شوید و اطلاعات دیتابیس ساخته‌شده را وارد کنید:

```ini
DB_CONNECTION=mysql
DB_HOST=DB_HOST_LIARA
DB_PORT=DB_PORT_LIARA
DB_DATABASE=DB_NAME_LIARA
DB_USERNAME=DB_USER_LIARA
DB_PASSWORD=DB_PASS_LIARA
```

---

### ۲. اجرای مایگریشن‌ها (Migrations & Seeders)
برای اجرای خودکار مایگریشن‌ها در هر بار استقرار، می‌توانید دستور زیر را در فایل `liara.json` قرار دهید:

```json
{
  "platform": "laravel",
  "laravel": {
    "webserver": "nginx"
  },
  "hook": "php artisan migrate --force"
}
```

یا از طریق **کنسول تحت وب (خط فرمان)** لیارا مستقیماً دستور را دستی اجرا کنید:
```bash
php artisan migrate --force
```

> [!TIP]
> برای امنیت بیشتر، همیشه از فلگ `--force` در محیط پروداکشن برای مایگریشن‌ها استفاده کنید.
"""
    # 4. Topic: Disk / Storage
    elif "دیسک" in query or "disk" in query.lower() or "storage" in query.lower() or "ذخیره" in query:
        formatted_reply = """### 💾 راهنمای ایجاد و اتصال دیسک ابری دائمی (Persistent Disk) در لیارا

فایل‌سیستم برنامه‌ها در لیارا به صورت پیش‌فرض **ناپایدار (Stateless)** است. برای ذخیره دائمی فایل‌های آپلودی کاربران، فایل‌های مدیا یا دیتابیس‌های فایلی مانند SQLite، باید از دیسک ابری استفاده کنید.

---

### ۱. ساخت دیسک در پنل لیارا
1. وارد داشبورد برنامه خود شوید.
2. از منوی سمت راست، گزینه **دیسک‌ها (Disks)** را انتخاب نمایید.
3. روی **ایجاد دیسک جدید** کلیک کرده و نامی برای آن تعیین کنید (مثلاً `uploads_disk`).

---

### ۲. اتصال دیسک در فایل `liara.json`
فایل `liara.json` را در ریشه پروژه باز کرده و بخش `disks` را به آن اضافه کنید:

```json
{
  "platform": "laravel",
  "disks": [
    {
      "name": "uploads_disk",
      "mountTo": "/var/www/html/storage/app/public"
    }
  ]
}
```

---

### ۳. استقرار مجدد برنامه
پس از ذخیره فایل، برنامه را مجدداً مستقر کنید تا دیسک به مسیر مورد نظر متصل شود:
```bash
liara deploy
```
"""
    # 5. Topic: GitHub Actions / CI/CD
    elif "github" in query.lower() or "actions" in query.lower() or "ci/cd" in query.lower() or "گیت‌هاب" in query or "اتوماسیون" in query:
        formatted_reply = """### 🚀 راهنمای استقرار خودکار با GitHub Actions در لیارا

با استفاده از سرویس GitHub Actions می‌توانید فرآیند استقرار خودکار را با هر بار `git push` به شاخه اصلی فعال نمایید.

---

### ۱. دریافت API Token از لیارا
1. وارد حساب کاربری خود در لیارا شوید.
2. روی تصویر پروفایل کلیک کرده و وارد بخش **دسترسی به API** شوید.
3. یک کلید جدید ایجاد کرده و مقدار آن را کپی نمایید.

---

### ۲. ذخیره Token در GitHub Secrets
1. در ریپازیتوری گیت‌هاب خود، به مسیر **Settings > Secrets and variables > Actions** بروید.
2. روی **New repository secret** کلیک کنید.
3. نام متغیر را `LIARA_API_TOKEN` و مقدار آن را کلید کپی‌شده بگذارید.

---

### ۳. ایجاد فایل ورک‌فلو (`.github/workflows/liara.yml`)
فایل زیر را در پوشه `.github/workflows/` پروژه خود ایجاد نمایید:

```yaml
name: Deploy to Liara Cloud

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Liara CLI
        run: npm install -g @liara/cli
        
      - name: Deploy to Liara
        env:
          LIARA_TOKEN: ${{ secrets.LIARA_API_TOKEN }}
        run: liara deploy --app my-app-name --api-token $LIARA_TOKEN --detach
```
"""
    # 6. General RAG Synthesis with Clean Formatting
    else:
        top_doc = results[0] if results else None
        if top_doc:
            # Clean raw text from markdown garbage
            raw_text = top_doc['text']
            raw_text = re.sub(r'AddOutputFilterByType[^\n]+', '', raw_text)
            raw_text = re.sub(r'\s{3,}', '\n\n', raw_text).strip()
            
            formatted_reply = f"""### 📖 {top_doc['title']} — {top_doc['section']}

{raw_text}

---

### 💻 دستورات و کدهای اجرایی:
"""
            if top_doc['codes']:
                for code in top_doc['codes'][:2]:
                    formatted_reply += f"\n```bash\n{code.strip()}\n```\n"
            else:
                formatted_reply += "\n```bash\nliara deploy\n```\n"
                
            if len(results) > 1:
                formatted_reply += "\n### 📌 نکات تکمیلی و راهنماهای مرتبط:\n"
                for extra in results[1:3]:
                    extra_clean = re.sub(r'AddOutputFilterByType[^\n]+', '', extra['text'])[:120].strip()
                    formatted_reply += f"- **[{extra['title']} — {extra['section']}]({extra['url']}):** {extra_clean}...\n"
        else:
            formatted_reply = """مستندات دقیقی برای این عبارت یافت نشد. لطفاً نام پلتفرم (مانند NodeJS، Laravel، Django، Docker، PostgreSQL) یا کلمه کلیدی دقیق‌تری را وارد نمایید."""

    response_data = {
        "reply": formatted_reply,
        "citations": citations,
        "suggestions": suggestions,
        "latency_ms": 12,
        "platform_detected": platform_filter or (results[0]['platform'] if results else 'general')
    }

    # Save to cache
    RESPONSE_CACHE[cache_key] = response_data
    return response_data

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    retriever.load_knowledge_base(KNOWLEDGE_BASE_PATH)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "liara-agentic-rag-assistant",
        "corpus_docs": retriever.corpus_size,
        "platforms": list(retriever.platforms)
    }

@app.post("/api/chat")
async def chat_endpoint(payload: Dict[str, Any]):
    query = payload.get("message", "").strip()
    platform = payload.get("platform", None)
    if not query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")
    
    start_t = time.time()
    result = await process_agent_chat(query, platform)
    result["latency_ms"] = round((time.time() - start_t) * 1000, 1)
    return result

@app.post("/api/generate-config")
def config_generator_endpoint(payload: Dict[str, Any]):
    platform = payload.get("platform", "node")
    port = int(payload.get("port", 3000))
    disk_name = payload.get("disk_name", "")
    mount_path = payload.get("mount_path", "")
    app_name = payload.get("app_name", "my-app")

    cfg = generate_liara_json(platform, port, disk_name, mount_path, app_name)
    return {"status": "success", "config": cfg}

@app.get("/api/search")
def search_endpoint(q: str, platform: Optional[str] = None, limit: int = 5):
    results = retriever.search(q, platform_filter=platform, top_k=limit)
    return {"query": q, "count": len(results), "results": results}

# ---------------------------------------------------------------------------
# HTML Single Page Portal & Favicon
# ---------------------------------------------------------------------------
@app.get("/favicon.ico")
@app.head("/favicon.ico")
@app.get("/favicon.svg")
@app.head("/favicon.svg")
def serve_favicon():
    svg_path = os.path.join(STATIC_DIR, "favicon.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="image/svg+xml")
    return Response(content="<svg xmlns='http://www.w3.org/2000/svg'></svg>", media_type="image/svg+xml")

@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def serve_portal():
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Liara AI Assistant Portal Loading...</h1>"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3012))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
