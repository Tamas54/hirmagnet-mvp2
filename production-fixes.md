# HírMagnet Production Deployment Fixes

## 1. Database Connection Fix

**Fájl:** `database/db.py` vagy ahol az SQLAlchemy engine van

**Probléma:** Connection pool limit
**Megoldás:** Production-safe SQLite konfiguráció

```python
# ELŐTTE (problémás):
engine = create_engine("sqlite:///data/hirmagnet.db")

# UTÁNA (javított):
import os

if os.environ.get("RENDER"):
    # Production: minimális connection pool
    engine = create_engine(
        "sqlite:///data/hirmagnet.db",
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )
else:
    # Development: normál konfiguráció
    engine = create_engine("sqlite:///data/hirmagnet.db")
```

## 2. Deployment Script Fix

**Fájl:** `hirmagnet_newspaper.py`

**Probléma:** Production-ban ne fusson a teljes newspaper logika
**Megoldás:** Environment-specific indítás

```python
if __name__ == "__main__":
    if os.environ.get("RENDER"):
        # RENDER PRODUCTION MODE
        print("🚀 HírMagnet RENDER Production Mode")
        
        # Csak FastAPI indítása
        port = int(os.environ.get("PORT", 8000))
        import uvicorn
        from api.main import app
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    else:
        # DEVELOPMENT MODE 
        sys.exit(main())
```

## 3. Content Generation Endpoint

**Fájl:** `api/main.py` vagy routes fájl

**Hozzáadni egy admin endpoint-ot:**

```python
@app.post("/api/admin/generate-content")
async def trigger_content_generation():
    """Manual content generation trigger for production"""
    try:
        import subprocess
        import sys
        
        # Background process indítása
        subprocess.Popen([
            sys.executable, 
            "test_master.py", 
            "--mode", "quick", 
            "--generate-content"
        ])
        
        return {"status": "Content generation started"}
    except Exception as e:
        return {"error": str(e)}
```

## 4. Environment Variables

**Render Dashboard-on beállítandó:**

```
RENDER=true
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
STRIPE_PUBLIC_KEY=your_key_here
STRIPE_SECRET_KEY=your_key_here
```

## 5. Health Check Endpoint

**API-hoz hozzáadni:**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.environ.get("RENDER", "development"),
        "database": "connected" if check_db_connection() else "error"
    }
```

## 6. Startup Content Generation

**Opcionális: auto content generation indítása**

```python
# api/main.py startup event
@app.on_event("startup")
async def startup_event():
    if os.environ.get("RENDER"):
        # 30 másodperc után indítson content generation-t
        import asyncio
        asyncio.create_task(delayed_content_generation())

async def delayed_content_generation():
    await asyncio.sleep(30)  # Várj hogy a szerver elinduljon
    # Trigger content generation
```

## Deployment Steps

1. **Ezeket a fixeket implementálni**
2. **Git commit & push**
3. **Render újra deploy**
4. **Environment variables beállítása**
5. **Manual content generation trigger:** `/api/admin/generate-content`

## Testing

Render deployment után tesztelni:
- `GET /health` - szerver állapot
- `GET /api/articles` - üres de működik
- `POST /api/admin/generate-content` - manual trigger
- Várni 5-10 percet a cikkgenerálásra
- `GET /api/articles` újra - most már cikkekkel