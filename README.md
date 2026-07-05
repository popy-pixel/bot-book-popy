📖 1. מהו הפרויקט ולמי הוא שימושי
BOT-BOOK-POPY הוא מסגרת עבודה (Framework) מתקדמת לניהול אוטומציה של חשבונות פייסבוק. המערכת מספקת ניהול מרובה חשבונות בבידוד מוחלט, אמולציה של דפדפן אנושי אמיתי, ביצוע פעולות אוטומטיות (פרסום, תגובות, לייקים), וממשק ווב מלא לניהול והפקחה.
למי הוא שימושי:
מפתחי אוטומציה — למידה של טכניקות אנטי-גילוי מתקדמות
חוקרי אבטחה — מחקר של מערכות זיהוי בוטים
מנהלי רשתות חברתיות — ניהול מספר חשבונות בצורה מאורגנת
סטודנטים — לימוד ארכיטקטורת תוכנה מתקדמת
מהנדסי DevOps — דוגמה למערכת מבוזרת עם תורים ו-Workers
⚠️ אזהרה: הפרויקט נועד למטרות חינוכיות ומחקריות בלבד. השימוש בו נגד תנאי השירות של פייסבוק הוא על אחריות המשתמש בלבד.
🧠 2. אופי הקוד והידעוד שלו
אופי הקוד:
שפה: Python 3.12 (Backend) + React (Frontend)
סגנון: אסינכרוני (Async/Await) ברובו
ארכיטקטורה: Microservices-lite עם הפרדת שכבות
בידוד: כל חשבון רץ בדפדפן נפרד לחלוטין
התחמקות: 16 טכניקות שונות נגד זיהוי בוטים
טכנולוגיות ליבה:
FastAPI — מסגרת ווב מהירה עם תמיכה ב-async
Playwright — אוטומציה של דפדפן (מחליף את Selenium)
Celery + Redis — תור משימות מבוזר
SQLAlchemy Async — ORM אסינכרוני למסד נתונים
Pydantic — וולידציה של נתונים
16 טכניקות אנטי-גילוי:
Spoofing של Navigator, WebGL Spoofing, Canvas Noise, WebRTC Block, Chrome Runtime APIs, Permission API, Battery API, Font Fingerprinting, Screen Properties, iframe Patch, Performance Cleanup, toString Patching, User-Agent Rotation, Viewport Randomization, Timezone Spoofing, Hardware Concurrency
🏗️ 3. איך עובד הקוד — הסבר ארכיטקטורה
תרשים זרימת נתונים:
plain
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
תהליך ביצוע משימה:
משתמש יוצר משימה דרך ה-UI
ה-Frontend שולח בקשה ל-API
FastAPI שומר את המשימה ב-DB (סטטוס: PENDING)
Celery Worker מושך את המשימה מהתור (סטטוס: RUNNING)
Browser Manager יוצר/משתמש בסשן מבודד
Stealth Engine מחיל חתימת דפדפן ייחודית
Humanoid Engine מבצע פעולות כמו בן אדם
Facebook Actions מבצע את הפעולה המבוקשת
תוצאה נשמרת ב-DB + WebSocket מעדכן את ה-UI
🗂️ 4. דיאגרמת קבצים ומבנה הפרויקט
plain
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
│   │   ├── 📄 logs.py               ← לוגי פעילות
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
🚀 5. הוראות התקנה מלאות
אפשרות א: WSL (Ubuntu) — מומלץ!
שלב 1 — פתיחת WSL:
bash
wsl
# או
wsl -d Ubuntu
שלב 2 — התקנת תלויות:
bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv redis-server git curl
שלב 3 — העתקת קבצים:
bash
mkdir -p ~/projects
cp -r /mnt/c/Users/USERNAME/bot-book-popy ~/projects/
cd ~/projects/bot-book-popy
שלב 4 — הגדרת סביבה:
bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
mkdir -p data/profiles data/screenshots data/logs
cp .env.example .env
שלב 5 — עריכת .env:
bash
nano .env
תוכן מינימלי:
env
HOST=0.0.0.0
PORT=8000
DEBUG=True
SECRET_KEY=change-this-to-something-random-123456
DATABASE_URL=sqlite:///data/botbook.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
אפשרות ב: Docker Compose (הכי פשוט!)
bash
cd ~/projects/bot-book-popy
docker-compose up -d
🖥️ 6. איך לפתוח ולהריץ את הקבצים
פתח 4 טרמינלים במקביל:
Table
טרמינל	פקודה	תפקיד
#1	sudo service redis-server start	Redis Server
#2	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000	FastAPI Backend
#3	celery -A app.workers.celery_app worker --loglevel=info --concurrency=4	Celery Worker
#4	cd frontend && npm install && npm run dev	React Frontend
גישה מדפדפן Windows:
ממשק המשתמש: http://localhost:3000
API Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/health
📋 פקודות שימושיות
Table
פעולה	פקודה
הפעלת סביבה וירטואלית	source venv/bin/activate
יציאה מהסביבה	deactivate
בדיקת Redis	redis-cli ping
מחיקת מסד נתונים	rm data/botbook.db
רשימת תהליכים	ps aux | grep python
הריגת תהליך	kill -9 PID
