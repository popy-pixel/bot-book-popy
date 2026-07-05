

content = """# BOT-BOOK-POPY
## מסגרת עבודה מתקדמת לניהול אוטומציה של חשבונות פייסבוק

---

## 📖 1. סקירה כללית

### מהו הפרויקט?

**BOT-BOOK-POPY** היא מסגרת עבודה (Framework) מתקדמת לניהול אוטומציה של חשבונות פייסבוק. המערכת מספקת:

| תכונה | תיאור |
|-------|--------|
| **ניהול מרובה חשבונות** | בידוד מוחלט בין כל חשבון |
| **אמולציה אנושית** | חיקוי של דפדפן אנושי אמיתי |
| **פעולות אוטומטיות** | פרסום, תגובות, לייקים |
| **ממשק ווב מלא** | ניהול והפקחה דרך דפדפן |

### למי הוא שימושי?

| קהל יעד | מטרה |
|---------|------|
| 👨‍💻 **מפתחי אוטומציה** | למידה של טכניקות אנטי-גילוי מתקדמות |
| 🔒 **חוקרי אבטחה** | מחקר של מערכות זיהוי בוטים |
| 📊 **מנהלי רשתות חברתיות** | ניהול מספר חשבונות בצורה מאורגנת |
| 🎓 **סטודנטים** | לימוד ארכיטקטורת תוכנה מתקדמת |
| ⚙️ **מהנדסי DevOps** | דוגמה למערכת מבוזרת עם תורים ו-Workers |

> ⚠️ **אזהרה משפטית**: הפרויקט נועד **למטרות חינוכיות ומחקריות בלבד**. השימוש בו נגד תנאי השירות של פייסבוק הוא על אחריות המשתמש בלבד.

---

## 🧠 2. אופי הקוד והטכנולוגיות

### מפרט טכני

| פרמטר | פרט |
|-------|-----|
| **שפת Backend** | Python 3.12 |
| **שפת Frontend** | React |
| **סגנון תכנות** | אסינכרוני (Async/Await) |
| **ארכיטקטורה** | Microservices-lite עם הפרדת שכבות |
| **בידוד חשבונות** | כל חשבון רץ בדפדפן נפרד לחלוטין |
| **טכניקות אנטי-גילוי** | 16 טכניקות שונות |

### טכנולוגיות ליבה

| טכנולוגיה | תפקיד |
|-----------|-------|
| **FastAPI** | מסגרת ווב מהירה עם תמיכה ב-async |
| **Playwright** | אוטומציה של דפדפן (מחליף את Selenium) |
| **Celery + Redis** | תור משימות מבוזר |
| **SQLAlchemy Async** | ORM אסינכרוני למסד נתונים |
| **Pydantic** | וולידציה של נתונים |

### 16 טכניקות אנטי-גילוי

| # | טכניקה | תיאור |
|---|--------|-------|
| 1 | **Navigator Spoofing** | שינוי אובייקט Navigator |
| 2 | **WebGL Spoofing** | שינוי חתימת WebGL |
| 3 | **Canvas Noise** | הוספת רעש ל-Canvas Fingerprinting |
| 4 | **WebRTC Block** | חסימת דליפת IP דרך WebRTC |
| 5 | **Chrome Runtime APIs** | אמולציה של APIs של Chrome |
| 6 | **Permission API** | ניהול הרשאות דפדפן |
| 7 | **Battery API** | אמולציה של Battery Status API |
| 8 | **Font Fingerprinting** | ניהול רשימת גופנים |
| 9 | **Screen Properties** | שינוי מאפייני מסך |
| 10 | **iframe Patch** | תיקון חשיפה ב-iframes |
| 11 | **Performance Cleanup** | ניקוי נתוני ביצועים |
| 12 | **toString Patching** | תיקון toString של פונקציות |
| 13 | **User-Agent Rotation** | סיבוב User-Agent |
| 14 | **Viewport Randomization** | רנדומיזציה של גודל חלון |
| 15 | **Timezone Spoofing** | שינוי אזור זמן |
| 16 | **Hardware Concurrency** | אמולציה של מספר ליבות מעבד |

---

## 🏗️ 3. ארכיטקטורת המערכת

### תרשים זרימת נתונים

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   משתמש (UI)    │────▶│  React Frontend  │────▶│  FastAPI API    │
│                 │     │  (localhost:3000)│     │  (localhost:8000)│
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                              ┌──────────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL/   │
                    │    SQLite DB    │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  Celery Worker  │◀────┐
                    │   (Redis Queue) │     │
                    └────────┬────────┘     │
                             ▼              │
                    ┌─────────────────┐      │
                    │  Browser Manager │      │
                    │  (Playwright)    │      │
                    └────────┬────────┘      │
              ┌──────────────┼───────────────┘
              ▼              ▼
    ┌──────────────┐  ┌──────────────┐
    │  Account #1  │  │  Account #2  │  ...  Account #N
    │  (Profile A) │  │  (Profile B) │
    │  + Proxy #1  │  │  + Proxy #2  │
    │  + UA Chrome │  │  + UA Firefox│
    │  + Fingerprint│  │  + Fingerprint│
    └──────────────┘  └──────────────┘
```

### תהליך ביצוע משימה (צעד אחר צעד)

| שלב | פעולה | רכיב |
|-----|-------|------|
| 1 | המשתמש יוצר משימה דרך ה-UI | React Frontend |
| 2 | ה-Frontend שולח בקשה ל-API | FastAPI |
| 3 | FastAPI שומר את המשימה ב-DB | PostgreSQL/SQLite |
| 4 | סטטוס: **PENDING** | - |
| 5 | Celery Worker מושך את המשימה מהתור | Celery + Redis |
| 6 | סטטוס: **RUNNING** | - |
| 7 | Browser Manager יוצר/משתמש בסשן מבודד | Playwright |
| 8 | Stealth Engine מחיל חתימת דפדפן ייחודית | Stealth Engine |
| 9 | Humanoid Engine מבצע פעולות כמו בן אדם | Humanoid Engine |
| 10 | Facebook Actions מבצע את הפעולה המבוקשת | Facebook Actions |
| 11 | התוצאה נשמרת ב-DB | PostgreSQL/SQLite |
| 12 | WebSocket מעדכן את ה-UI בזמן אמת | WebSocket |

---

## 🗂️ 4. מבנה הפרויקט

### עץ קבצים מלא

```
bot-book-popy/
│
├── 📁 app/                          ← קוד הליבה של האפליקציה
│   │
│   ├── 📄 main.py                   ← נקודת כניסה - FastAPI + Lifespan
│   ├── 📄 config.py                 ← הגדרות מרכזיות
│   │
│   ├── 📁 api/                      ← נקודות קצה (Routes) של ה-API
│   │   ├── 📄 accounts.py           ← CRUD חשבונות + בדיקת התחברות
│   │   ├── 📄 tasks.py              ← CRUD משימות + ביטול
│   │   ├── 📄 dashboard.py          ← סטטיסטיקות ונתונים
│   │   ├── 📄 logs.py               ← לוגי פעולות
│   │   ├── 📄 settings.py           ← הגדרות גלובליות
│   │   └── 📄 websocket.py          ← עדכונים בזמן אמת
│   │
│   ├── 📁 core/                     ← מנועי הליבה (הלב של המערכת)
│   │   ├── 📄 stealth_engine.py     ← מנוע אנטי-גילוי (16 טכניקות)
│   │   ├── 📄 humanoid.py           ← אמולציה התנהגות אנושית
│   │   ├── 📄 browser_manager.py    ← ניהול דפדפנים מבודדים
│   │   ├── 📄 proxy_rotator.py      ← ניהול פרוקסי + בדיקת בריאות
│   │   └── 📄 captcha_solver.py     ← זיהוי ופתרון CAPTCHA
│   │
│   ├── 📁 services/                 ← שכבת העסקים (Business Logic)
│   │   ├── 📄 facebook_actions.py   ← כל הפעולות בפייסבוק
│   │   ├── 📄 facebook_selectors.py ← בוררי CSS חכמים עם fallback
│   │   ├── 📄 natural_language_parser.py ← פירוש הוראות בשפה טבעית
│   │   ├── 📄 rate_limiter.py       ← מגבלת קצב לחשבון
│   │   └── 📄 notification_service.py ← התראות (Webhook, Email)
│   │
│   ├── 📁 models/                   ← שכבת מסד הנתונים
│   │   ├── 📄 database.py           ← מנוע SQLAlchemy Async + Session
│   │   ├── 📄 models.py             ← מודלי ORM (טבלאות)
│   │   └── 📄 schemas.py            ← מודלי Pydantic (וולידציה)
│   │
│   ├── 📁 workers/                  ← עובדים ברקע (Celery)
│   │   ├── 📄 celery_app.py         ← הגדרות Celery
│   │   └── 📄 task_worker.py        ← מבצע משימות + ניהול שגיאות
│   │
│   ├── 📁 utils/                    ← כלי עזר משותפים
│   │   ├── 📄 crypto.py             ← הצפנת סיסמאות ועוגיות
│   │   ├── 📄 logger.py             ← לוגים מובנים ב-JSON
│   │   ├── 📄 screenshot_utils.py   ← צילומי מסך עם הערות
│   │   └── 📄 validators.py         ← וולידציה של קלט
│   │
│   └── 📁 static/                   ← קבצים סטטיים
│
├── 📁 frontend/                     ← ממשק המשתמש (React)
│   ├── 📄 package.json              ← חבילות npm
│   ├── 📄 vite.config.js            ← הגדרות Vite
│   ├── 📄 tailwind.config.js        ← הגדרות Tailwind CSS
│   ├── 📄 index.html                ← דף HTML ראשי
│   └── 📁 src/
│       ├── 📄 main.jsx              ← נקודת כניסה React
│       ├── 📄 App.jsx               ← ניתוב ראשי
│       ├── 📄 index.css             ← סגנונות גלובליים
│       ├── 📁 components/           ← רכיבי UI
│       │   ├── 📄 Navbar.jsx        ← תפריט ניווט
│       │   ├── 📄 Dashboard.jsx     ← לוח מחוונים
│       │   ├── 📄 AccountManager.jsx ← ניהול חשבונות
│       │   ├── 📄 TaskCreator.jsx   ← יצירת משימות
│       │   ├── 📄 LiveMonitor.jsx   ← מעקב חי
│       │   └── 📄 SettingsPanel.jsx ← הגדרות מערכת
│       ├── 📁 hooks/                ← Hooks מותאמים אישית
│       ├── 📁 services/             ← שירותי API
│       └── 📁 context/              ← Context API
│
├── 📁 data/                         ← נתוני זמן ריצה (לא ב-git)
│   ├── 📁 profiles/                 ← פרופילי דפדפן לכל חשבון
│   ├── 📁 screenshots/              ← צילומי מסך
│   └── 📁 logs/                     ← קבצי לוג
│
├── 📁 scripts/                      ← סקריפטים
│   └── 📄 setup.sh                  ← סקריפט התקנה אוטומטית
│
├── 📄 .env.example                  ← תבנית משתני סביבה
├── 📄 .gitignore                    ← קבצים להתעלמות
├── 📄 requirements.txt              ← חבילות Python
├── 📄 Dockerfile                    ← בניית Docker
├── 📄 docker-compose.yml            ← הרכבה מלאה ב-Docker
└── 📄 README.md                     ← תיעוד
```

---

## 🚀 5. הוראות התקנה

### אפשרות א: WSL (Ubuntu) — מומלץ!

#### שלב 1 — פתיחת WSL
```bash
wsl
# או
wsl -d Ubuntu
```

#### שלב 2 — התקנת תלויות
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv redis-server git curl
```

#### שלב 3 — העתקת קבצים
```bash
mkdir -p ~/projects
cp -r /mnt/c/Users/USERNAME/bot-book-popy ~/projects/
cd ~/projects/bot-book-popy
```

#### שלב 4 — הגדרת סביבה
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
mkdir -p data/profiles data/screenshots data/logs
cp .env.example .env
```

#### שלב 5 — עריכת קובץ `.env`
```bash
nano .env
```

**תוכן מינימלי:**
```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
SECRET_KEY=change-this-to-something-random-123456
DATABASE_URL=sqlite:///data/botbook.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

### אפשרות ב: Docker Compose (הכי פשוט!)

```bash
cd ~/projects/bot-book-popy
docker-compose up -d
```

---

## 🖥️ 6. הפעלת המערכת

### פתיחת 4 טרמינלים במקביל

| טרמינל | פקודה | תפקיד |
|--------|-------|-------|
| **#1** | `sudo service redis-server start` | Redis Server |
| **#2** | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | FastAPI Backend |
| **#3** | `celery -A app.workers.celery_app worker --loglevel=info --concurrency=4` | Celery Worker |
| **#4** | `cd frontend && npm install && npm run dev` | React Frontend |

### גישה מדפדפן Windows

| שירות | כתובת |
|-------|-------|
| 🖥️ ממשק המשתמש | [http://localhost:3000](http://localhost:3000) |
| 📚 API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ✅ בדיקת בריאות | [http://localhost:8000/health](http://localhost:8000/health) |

---

## 📋 פקודות שימושיות

| פעולה | פקודה |
|-------|-------|
| הפעלת סביבה וירטואלית | `source venv/bin/activate` |
| יציאה מהסביבה | `deactivate` |
| בדיקת Redis | `redis-cli ping` |
| מחיקת מסד נתונים | `rm data/botbook.db` |
| רשימת תהליכים | `ps aux | grep python` |
| הריגת תהליך | `kill -9 PID` |

---

## 🎯 סיכום

BOT-BOOK-POPY היא מערכת מתקדמת המשלבת:
- ✅ ארכיטקטורת Microservices-lite
- ✅ 16 טכניקות אנטי-גילוי
- ✅ בידוד מוחלט בין חשבונות
- ✅ ממשק ווב מודרני (React + FastAPI)
- ✅ תור משימות מבוזר (Celery + Redis)
- ✅ אמולציה התנהגות אנושית

> **הערה חשובה**: זכור תמיד כי השימוש בכלי זה נגד תנאי השירות של פלטפורמות כמו פייסבוק עלול לגרום לחסימת חשבונות ופעולות משפטיות. השתמש בו אך ורק למטרות חוקיות, חינוכיות ומחקריות.
"""

# Save the formatted content
with open('/mnt/agents/output/BOT-BOOK-POPY_Documentation.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ הקובץ נשמר בהצלחה!")
print(f"📄 אורך התיעוד: {len(content):,} תווים")
