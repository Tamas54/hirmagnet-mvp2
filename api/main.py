# api/main.py - JAVÍTOTT VERZIÓ - DIRECT ARTICLE ROUTE + CACHE HEADERS
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
import os
import json

# Database imports
from database.db import get_db, create_tables, SessionLocal
from database.models import Article, User, SocialPost, SiteStats, ProcessingLog

# ROUTES IMPORT ÉS INCLUDE
from api.routes import router as api_router

# FastAPI app
app = FastAPI(
    title="HírMagnet API",
    description="AI-powered Hungarian News Portal with Premium Features",
    version="2.0.0"
)

# Database initialization
try:
    create_tables()
    print("✅ Database tables created/verified")
except Exception as e:
    print(f"⚠️ Database setup warning: {e}")

# 🧲 HERR CLAUS CACHE-KILLER MIDDLEWARE - KRITIKUS!
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """
    Deutsche Präzision Cache-Killer Middleware
    Minden API endpoint és statikus fájl no-cache header-t kap
    """
    response = await call_next(request)
    
    # API endpoint-ok (beleértve DataCollector-t is)
    if request.url.path.startswith('/api/'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Last-Modified"] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Extra cache busting header
        response.headers["X-Cache-Control"] = "no-cache"
        
        print(f"🧲 CACHE-KILLER applied to API: {request.url.path}")
    
    # HTML/JS/CSS fájlok
    elif any(request.url.path.endswith(ext) for ext in ['.html', '.js', '.css']):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        print(f"🧲 CACHE-KILLER applied to static: {request.url.path}")
    
    # Különleges behandlung für root endpoints
    elif request.url.path in ['/', '/index.html', '/article-view.html']:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        print(f"🧲 CACHE-KILLER applied to root: {request.url.path}")
    
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production-ban korlátozd!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - HTML fájlok kiszolgálásához
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# ⚡ KRITIKUS: ROUTES INCLUDE
app.include_router(api_router, prefix="/api")

# === DIRECT ARTICLE TEST ROUTE ===
@app.get("/direct-article")
async def direct_article(id: int = Query(...), db: Session = Depends(get_db)):
    """Direct article loader - bypasses static files"""
    try:
        # Get article from database
        article = db.query(Article).filter(Article.id == id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Cikk nem található")
        
        # Increment view count
        article.view_count += 1
        db.commit()
        
        # Return HTML with article data
        html_content = f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- 🧲 HERR CLAUS CACHE-KILLER HEADERS -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    
    <title>{article.title} - HírMagnet</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success {{ background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }}
        .title {{ font-size: 2.5rem; margin-bottom: 20px; color: #1a4314; line-height: 1.3; }}
        .meta {{ color: #666; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .content {{ line-height: 1.8; margin-bottom: 20px; font-size: 1.1rem; }}
        .back-btn {{ background: #3A7BCE; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        .debug {{ background: #000; color: #0f0; padding: 10px; font-family: monospace; margin-bottom: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="debug">
            🧲 DIRECT ARTICLE ROUTE LOADED + CACHE-KILLER ACTIVE<br>
            ✅ Article ID: {article.id}<br>
            ✅ Database Query: SUCCESS<br>
            ✅ Title: {article.title}<br>
            ✅ Source: {article.source}<br>
            ✅ Cache Headers: DISABLED<br>
            ✅ Timestamp: {datetime.now().strftime('%H:%M:%S')}
        </div>
        
        <div class="success">
            🎯 DIRECT ROUTE SUCCESS + NO-CACHE! Cikk ID: {article.id} sikeresen betöltve cache-killer-rel!
        </div>
        
        <h1 class="title">{article.title}</h1>
        
        <div class="meta">
            <strong>🆔 Article ID:</strong> {article.id}<br>
            <strong>📰 Forrás:</strong> {article.source}<br>
            <strong>📂 Kategória:</strong> {article.category}<br>
            <strong>👁️ Megtekintések:</strong> {article.view_count}<br>
            <strong>📅 Publikálva:</strong> {article.published_at or 'N/A'}<br>
            <strong>🤖 AI feldolgozva:</strong> {article.created_at}
        </div>
        
        <div class="content">
            <p><strong>Összefoglaló:</strong></p>
            <p>{article.summary or 'Nincs összefoglaló'}</p>
            
            {f'<p><strong>Eredeti tartalom:</strong></p><p>{article.original_content}</p>' if article.original_content else ''}
            
            <hr style="margin: 30px 0;">
            <p><a href="{article.url}" target="_blank" style="color: #3A7BCE; text-decoration: none; font-weight: bold;">
                🔗 Eredeti cikk megtekintése ({article.source})
            </a></p>
        </div>
        
        <a href="/" class="back-btn">← Vissza a főoldalra</a>
    </div>
    
    <script>
        console.log('🧲 DIRECT ROUTE ARTICLE LOADED + CACHE-KILLER ACTIVE:');
        console.log('ID:', {article.id});
        console.log('Title:', '{article.title}');
        console.log('Source:', '{article.source}');
        console.log('Cache-Control: DISABLED');
        
        // Confirmation alert
        setTimeout(() => {{
            alert(`🎯 DIRECT ROUTE + CACHE-KILLER SUCCESS!\\n\\nCikk ID: {article.id}\\nCím: {article.title}\\nForrás: {article.source}\\nCache: DISABLED\\n\\nEz a HELYES cikk?`);
        }}, 500);
    </script>
</body>
</html>
        """
        
        # Cache-killer headers a response-hoz is
        return HTMLResponse(
            content=html_content,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
            <head>
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
                <meta http-equiv="Pragma" content="no-cache">
                <meta http-equiv="Expires" content="0">
            </head>
            <body>
                <h1>HIBA + CACHE-KILLER</h1>
                <p>Cikk ID: {id}</p>
                <p>Hiba: {str(e)}</p>
                <p>Cache: DISABLED</p>
                <a href="/">Vissza</a>
            </body>
            </html>
            """,
            status_code=500,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache", 
                "Expires": "0"
            }
        )

# === MAIN ROUTES ===
@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Főoldal"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        # Fallback to static directory
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
    
    # Cache-killer headers
    return HTMLResponse(
        content=content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.get("/article-view.html", response_class=HTMLResponse)
async def article_view_page():
    """Article view HTML oldal"""
    try:
        with open("article-view.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        # Fallback to static directory
        try:
            with open("static/article-view.html", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Article view oldal nem található")
    
    # Cache-killer headers
    return HTMLResponse(
        content=content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.get("/rss-feed.html", response_class=HTMLResponse)
async def rss_feed_page():
    """RSS Feed view HTML oldal"""
    try:
        with open("rss-feed.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        # Fallback to static directory
        try:
            with open("static/rss-feed.html", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="RSS feed oldal nem található")
    
    # Cache-killer headers
    return HTMLResponse(
        content=content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    """Index.html explicit route"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
    
    # Cache-killer headers
    return HTMLResponse(
        content=content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

# === HEALTH CHECK ===
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Rendszer állapot ellenőrzés"""
    try:
        # Database check
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "version": "2.0.0",
            "cache_control": "disabled",
            "cache_killer": "active"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "cache_control": "disabled"
            },
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

# === ADMIN & HEALTH ENDPOINTS ===
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy",
        "environment": os.environ.get("RENDER", "development"),
        "database": db_status,
        "version": "2.0.0"
    }

@app.post("/api/admin/generate-content")
async def trigger_content_generation():
    """Manual content generation trigger for production"""
    try:
        import subprocess
        import sys
        
        # Background process indítása
        process = subprocess.Popen([
            sys.executable, 
            "test_master.py", 
            "--mode", "quick"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return {
            "status": "Content generation started", 
            "process_id": process.pid,
            "message": "Check /api/articles in 2-3 minutes for new content"
        }
    except Exception as e:
        return {"error": f"Failed to start content generation: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    print("🧲 STARTING HIRMAGNET API WITH CACHE-KILLER MIDDLEWARE")
    print("🎖️ Deutsche Präzision Cache Control: ACTIVE")
    print("✅ API Endpoints: NO-CACHE")
    print("✅ Static Files: NO-CACHE")  
    print("✅ HTML Pages: NO-CACHE")
    print("✅ DataCollector: NO-CACHE")
    print("🚀 Server starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)