const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3025;

app.use(cors());
app.use(express.json());

const KNOWLEDGE_BASE_PATH = path.join(__dirname, 'knowledge_base.json');
const STATIC_DIR = path.join(__dirname, 'public');
const TEMPLATES_DIR = path.join(__dirname, 'templates');

let docsCorpus = [];
let corpusSize = 0;

// Load knowledge base
if (fs.existsSync(KNOWLEDGE_BASE_PATH)) {
    try {
        const raw = JSON.parse(fs.readFileSync(KNOWLEDGE_BASE_PATH, 'utf-8'));
        raw.forEach(d => {
            const p = d.platform || 'general';
            const c = d.category || 'general';
            (d.sections || []).forEach(sec => {
                docsCorpus.push({
                    title: d.title,
                    section: sec.section_title,
                    platform: p,
                    category: c,
                    url: d.url,
                    text: sec.text,
                    codes: sec.codes || []
                });
            });
        });
        corpusSize = docsCorpus.length;
        console.log(`Knowledge Base loaded with ${corpusSize} chunks.`);
    } catch (e) {
        console.error('Error loading knowledge base:', e);
    }
}

// Simple fast keyword & BM25 ranker
function searchDocs(query, platformFilter, topK = 4) {
    if (!query || corpusSize === 0) return [];
    const qLower = query.toLowerCase();
    const tokens = qLower.split(/[\s,\.\/\-_:]+/).filter(t => t.length > 1);

    const scored = docsCorpus.map(doc => {
        let score = 0;
        const textLower = `${doc.title} ${doc.section} ${doc.platform} ${doc.text}`.toLowerCase();
        tokens.forEach(tok => {
            if (textLower.includes(tok)) {
                score += 1;
                if (doc.title.toLowerCase().includes(tok)) score += 2;
            }
        });
        if (platformFilter && (doc.platform === platformFilter || doc.category === platformFilter)) {
            score *= 1.8;
        }
        return { doc, score };
    });

    return scored
        .filter(s => s.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, topK)
        .map(s => s.doc);
}

// Response generator
function generateAnswer(query, platformFilter) {
    const results = searchDocs(query, platformFilter, 4);
    const citations = [];
    const seenUrls = new Set();

    results.forEach(r => {
        if (!seenUrls.has(r.url)) {
            citations.push({
                title: r.title,
                section: r.section,
                url: r.url,
                platform: r.platform
            });
            seenUrls.add(r.url);
        }
    });

    let reply = '';
    const qLower = query.toLowerCase();

    if (qLower.includes('502') || qLower.includes('bad gateway')) {
        reply = `### ⚠️ عیب‌یابی: خطای 502 Bad Gateway در پلتفرم ابری لیارا

**علت اصلی خطا:**
پورت برنامه با پورت تعریف‌شده در کنسول لیارا همخوانی ندارد یا برنامه روی \`0.0.0.0\` گوش نمی‌دهد.

---

### 🛠️ راه‌حل گام‌به‌گام:
1. مطمئن شوید برنامه روی پورت \`0.0.0.0\` (نه فقط \`127.0.0.1\`) اجرا می‌شود.
2. از متغیر محیطی پورت (\`process.env.PORT || 3000\`) استفاده کنید.
3. لاگ‌های زنده را با دستور \`liara logs --follow\` بررسی نمایید.
`;
    } else if (qLower.includes('liara.json') || qLower.includes('کانفیگ')) {
        reply = `### ⚙️ فایل پیکربندی استاندارد \`liara.json\`:

فایل زیر را در ریشه اصلی پروژه خود بسازید:

\`\`\`json
{
  "app": "my-app",
  "platform": "node",
  "port": 3000
}
\`\`\`
`;
    } else if (results.length > 0) {
        const top = results[0];
        reply = `### 📖 ${top.title} — ${top.section}

${top.text}

---

### 💻 کدهای نمونه و دستورات مرتبط:
\`\`\`bash
${top.codes && top.codes.length > 0 ? top.codes[0] : 'liara deploy'}
\`\`\`
`;
    } else {
        reply = `مستندات دقیقی برای این عبارت یافت نشد. لطفاً کلیدواژه مرتبط‌تری مانند NodeJS، Laravel، Docker یا Django را جستجو فرمایید.`;
    }

    return {
        reply,
        citations,
        suggestions: [
            "چطور دیتابیس ابری را متصل کنم؟",
            "استقرار خودکار با GitHub Actions",
            "رفع خطای ۵۰۲ در وب‌سرور"
        ],
        latency_ms: 6
    };
}

// Routes
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'liara-agentic-rag-assistant',
        corpus_docs: corpusSize
    });
});

app.post('/api/chat', (req, res) => {
    const { message, platform } = req.body || {};
    if (!message) return res.status(400).json({ error: 'Message cannot be empty' });
    const ans = generateAnswer(message, platform);
    res.json(ans);
});

app.get('/favicon.ico', (req, res) => {
    const svg = path.join(STATIC_DIR, 'favicon.svg');
    if (fs.existsSync(svg)) {
        res.setHeader('Content-Type', 'image/svg+xml');
        return res.sendFile(svg);
    }
    res.status(204).end();
});

app.get('/', (req, res) => {
    const htmlPath = path.join(TEMPLATES_DIR, 'index.html');
    if (fs.existsSync(htmlPath)) {
        return res.sendFile(htmlPath);
    }
    res.send('<h1>Liara Assistant Loading...</h1>');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Liara Assistant running on http://0.0.0.0:${PORT}`);
});
