# 🧲 HírMagnet - AI-Powered Hungarian News Portal

![HírMagnet Logo](static/background1.jpg)

## 📖 Áttekintés

A HírMagnet egy innovatív, mesterséges intelligenciával működő magyar hírportál, amely automatikusan gyűjti, feldolgozza és újraírja a híreket AI újságírókkal. A platform prémium funkciókat kínál hang alapú tartalommal és fejlett elemzésekkel.

## ✨ Főbb funkciók

### 🤖 AI Újságírók
- **Szakosított újságírók**: Politikai, sportos, gazdasági, technológiai témákban
- **Gemini és GPT-4o modellek**: Magas minőségű tartalomgenerálás
- **Személyiségprofilok**: Különböző stílusú írás (pl. Politikus Péter, Sportos Sára)

### 📰 Automatikus Hírek
- **RSS feed monitorozás**: Több mint 20 magyar hírforrás
- **Duplikátum szűrés**: Intelligens duplikátum felismerés
- **Kategorizálás**: Automatikus témakörök szerinti besorolás
- **Fontossági pontszám**: AI alapú relevanciabecslés

### 🎧 Prémium Funkciók
- **Text-to-Speech**: OpenAI TTS integráció
- **Audio cikkek**: Teljes cikkek hangfájlban
- **Előfizetési rendszer**: Stripe integráció
- **Fejlett szűrés**: Személyre szabott tartalomajánlás

### 🔧 Technikai Jellemzők
- **FastAPI backend**: Modern REST API
- **SQLite adatbázis**: Könnyű telepítés és karbantartás
- **Real-time frissítés**: 30 perces frissítési ciklus
- **Responsive design**: Mobil és desktop optimalizálás

## 🚀 Telepítés és Indítás

### 🌐 Production Deployment (Render)

**Live Demo:** [https://hirmagnet-mvp2.onrender.com](https://hirmagnet-mvp2.onrender.com)

A projekt automatikusan települ Render-re a GitHub push-kor. A production környezet:
- ✅ Optimalizált SQLite connection pool
- ✅ Automatikus adatbázis inicializáció  
- ✅ Environment-specific konfiguráció
- ✅ Manual content generation endpoint

**Production URL-ek:**
- Főoldal: `/`
- API dokumentáció: `/docs`
- Health check: `/health`
- Manual content generation: `POST /api/admin/generate-content`

### 🔧 Local Development

#### Előfeltételek
```bash
# Python 3.8+ szükséges
python --version

# Git klónozás
git clone https://github.com/Tamas54/hirmagnet-mvp2.git
cd hirmagnet
```

#### Függőségek telepítése
```bash
pip install -r requirements.txt
```

#### Környezeti változók
Hozzon létre egy `.env` fájlt:
```env
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

#### Development indítás
```bash
# Teljes funkcionalitással (cikkgenerálás + API)
python hirmagnet_newspaper.py

# Csak API szerver
python -m api.main
```

A rendszer automatikusan elindítja a webszervert a `http://localhost:8000` címen.

### 🎯 Production Usage

Production környezetben a cikkek nem generálódnak automatikusan. Manual trigger szükséges:

```bash
# cURL-lel
curl -X POST https://hirmagnet-mvp2.onrender.com/api/admin/generate-content

# Vagy böngészőben a /docs oldalon
```

2-3 perc után a cikkek megjelennek a `/api/articles` endpoint-on.

## 📁 Projekt struktúra

```
hirmagnet/
├── ai/                    # AI rendszerek
│   ├── journalists.py     # AI újságírók
│   ├── editorial_ai.py    # Szerkesztőségi AI
│   └── prompts/          # Prompt sablonok
├── api/                  # FastAPI backend
│   ├── main.py          # Fő alkalmazás
│   └── routes.py        # API végpontok
├── automation/          # Automatizálás
│   └── scheduler.py     # Időzített feladatok
├── database/           # Adatbázis
│   ├── models.py       # SQLAlchemy modellek
│   └── db.py          # Adatbázis kapcsolat
├── scraper/           # Hírek gyűjtése
│   └── news_scraper.py # RSS scraper
├── static/            # Frontend
│   ├── js/           # JavaScript
│   └── styles.css    # CSS stílusok
└── config/           # Konfigurációk
    ├── settings.py   # Beállítások
    └── sources.py    # Hírforrások
```

## 🔧 API Végpontok

### Publikus végpontok
- `GET /` - Főoldal
- `GET /api/articles` - Cikkek listája
- `GET /api/articles/{id}` - Konkrét cikk
- `GET /rss` - RSS feed

### Prémium végpontok
- `GET /api/premium/articles` - Prémium cikkek
- `GET /api/audio/{id}` - Audio fájlok
- `POST /api/subscribe` - Előfizetés

## 🤖 AI Újságírók

### Gemini Team
- **Politikus Péter**: Politikai hírek elemzése
- **Sportos Sára**: Sport hírek feldolgozása
- **Bulvár Beáta**: Szórakoztató hírek
- **Autós Aladár**: Gépjármű hírek

### Hybrid Experts
- **Gazdasági Géza**: Pénzügyi elemzések
- **Technológiai Tamás**: Tech hírek

### Premium Analysts
- **Analitikus Alfonz**: Mélyebb elemzések
- **Hírcsápa Henrik**: Investigatív újságírás

## 🛠️ Konfigurálás

### Hírforrások hozzáadása
A `config/sources.py` fájlban adhat hozzá új RSS feedeket:

```python
SOURCES = [
    {
        'name': 'Új Hírforrás',
        'url': 'https://example.com/rss',
        'category': 'politika'
    }
]
```

### AI beállítások
A `config/settings.py` fájlban módosíthatja:
- Összefoglaló maximális hossza
- TTS hang és sebesség
- Scraping gyakoriság

## 📊 Monitorozás

### Logok
A rendszer naplói a `data/logs/` mappában találhatók:
- `scraper.log` - Hírek gyűjtése
- `ai.log` - AI műveletek
- `api.log` - API hívások

### Adatbázis
SQLite adatbázis: `data/hirmagnet.db`
- Cikkek, felhasználók, előfizetések
- Statisztikák és használati adatok

## 💡 Fejlesztés

### Új AI újságíró hozzáadása
1. Prompt létrehozása a `ai/prompts/` mappában
2. Újságíró regisztrálása a `ai/journalists.py` fájlban
3. Kategória hozzárendelés

### Frontend módosítások
- JavaScript: `static/js/`
- Stílusok: `static/styles.css`
- HTML sablonok: `static/` mappa

## 🚨 Hibaelhárítás

### Gyakori problémák

#### 1. "QueuePool limit" hiba
```
QueuePool limit of size 5 overflow 10 reached
```
**Megoldás:** Production környezetben optimalizált connection pool fut, ezt a hibát javítottuk.

#### 2. Nincsenek cikkek a webapp-ban
**Megoldás:** Production-ban manual trigger szükséges:
```bash
curl -X POST https://hirmagnet-mvp2.onrender.com/api/admin/generate-content
```

#### 3. "no such table: articles" hiba  
**Megoldás:** Adatbázis automatikusan inicializálódik indításkor. Ha továbbra is hiba, ellenőrizd a `/health` endpoint-ot.

#### 4. Local development problémák
- **Port foglalt**: Módosítsd a portot a `config/settings.py` fájlban
- **API kulcsok**: Ellenőrizd a `.env` fájlt
- **Függőségek**: `pip install -r requirements.txt`

### Monitoring

**Health Check:**
```bash
curl https://hirmagnet-mvp2.onrender.com/health
```

**Response példa:**
```json
{
  "status": "healthy",
  "environment": "render", 
  "database": "connected",
  "version": "2.0.0"
}
```

### Hibák jelentése
Issues jelentése: [GitHub Issues](https://github.com/Tamas54/hirmagnet-mvp2/issues)

## 📄 Licenc

MIT License - részletek a LICENSE fájlban.

## 🤝 Közreműködés

1. Fork a projekt
2. Feature branch létrehozása
3. Commit változtatások
4. Push a branchre
5. Pull Request nyitása

---

**HírMagnet** - A jövő újságírása, ma! 🧲✨
