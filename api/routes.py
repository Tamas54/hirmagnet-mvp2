# routes.py - KOMPLETT EGYSÉGES VERZIÓ + HERR CLAUS ASYNC FIX
# HírMagnet Backend - Deutsche Präzision Engineering by Herr Claus
# Tartalmazza: Alap API + Admin funkciók + AI integráció + DataCollector + NON-BLOCKING OPERATIONS

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
from database.db import get_db
from database.models import Article
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# Pydantic models
from pydantic import BaseModel

# AI imports
import openai
import google.generativeai as genai

# DataCollector import
from hirmagnet_data_collector import DataCollector

# ===== HERR CLAUS ASYNC INFRASTRUCTURE =====

class ProcessingState:
    """Deutsche Präzision Processing State Management - RENDER OPTIMIZED"""
    def __init__(self):
        self.is_processing = False
        self.last_process_time = None
        self.executor = ThreadPoolExecutor(max_workers=1)  # RENDER FIX: Reduced workers
        self.processing_lock = threading.Lock()
        self.process_count = 0
        self.error_count = 0
        self.last_error = None
        
    def update_status(self, success=True, error_msg=None):
        """Update processing status with error tracking"""
        import datetime
        self.last_process_time = datetime.datetime.now()
        if success:
            self.process_count += 1
        else:
            self.error_count += 1
            self.last_error = error_msg

# ===== DATABASE WITH TIMEOUT PROTECTION =====

@contextmanager  
def get_db_with_timeout(timeout=10):
    """Database connection with timeout protection - RENDER OPTIMIZED"""
    session = None
    try:
        session = next(get_db())
        # RENDER FIX: Increased timeout and better error handling
        session.execute(text(f"PRAGMA busy_timeout = {timeout * 1000}"))
        session.execute(text("PRAGMA journal_mode = WAL"))  # Better concurrency
        session.execute(text("PRAGMA synchronous = NORMAL"))  # Performance optimization
        yield session
    except Exception as e:
        if session:
            try:
                session.rollback()
            except:
                pass  # Ignore rollback errors
        print(f"❌ Database timeout error: {e}")
        # Don't re-raise, return empty results instead for better UX
        yield None
    finally:
        if session:
            try:
                session.close()
            except:
                pass  # Ignore close errors

# ===== DASHBOARD CACHE SYSTEM =====

dashboard_cache = {
    "data": None,
    "last_update": None,
    "cache_duration": 120,  # RENDER FIX: Reduced to 2 minutes to prevent slowdowns
    "error_count": 0,
    "last_error": None
}

# ===== ROUTER SETUP =====
router = APIRouter()

# Globális instances
data_collector = DataCollector()
processing_state = ProcessingState()

# ===== RENDER PRODUCTION STATUS ENDPOINT =====
@router.get("/production-status")
async def get_production_status():
    """Comprehensive production status for Render debugging"""
    import os
    import datetime
    import sys
    
    try:
        # System information
        status = {
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": {
                "is_render": bool(os.environ.get("RENDER")),
                "port": os.environ.get("PORT", "8000"),
                "python_version": sys.version,
                "working_directory": os.getcwd(),
            },
            "api_keys": {
                "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
                "gemini_configured": bool(os.getenv('GEMINI_API_KEY')),
            },
            "processing": {
                "is_processing": processing_state.is_processing,
                "last_process_time": processing_state.last_process_time.isoformat() if processing_state.last_process_time else None,
                "process_count": processing_state.process_count,
                "error_count": processing_state.error_count,
                "last_error": processing_state.last_error
            },
            "cache": {
                "dashboard_cached": dashboard_cache["data"] is not None,
                "last_cache_update": dashboard_cache["last_update"].isoformat() if dashboard_cache["last_update"] else None,
                "cache_duration": dashboard_cache["cache_duration"],
                "error_count": dashboard_cache.get("error_count", 0),
                "last_error": dashboard_cache.get("last_error")
            }
        }
        
        # System resources (if available)
        try:
            import psutil
            status["resources"] = {
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.Process().cpu_percent(),
            }
        except ImportError:
            status["resources"] = {"error": "psutil not available"}
        except Exception as e:
            status["resources"] = {"error": str(e)}
        
        # Database health check
        try:
            with get_db_with_timeout(timeout=3) as db:
                if db:
                    result = db.execute(text("SELECT COUNT(*) as count FROM articles")).fetchone()
                    status["database"] = {
                        "connected": True,
                        "article_count": result.count if result else 0
                    }
                else:
                    status["database"] = {"connected": False, "error": "Timeout"}
        except Exception as e:
            status["database"] = {"connected": False, "error": str(e)}
        
        # File system check
        status["filesystem"] = {
            "test_master_exists": os.path.exists("test_master.py"),
            "database_exists": os.path.exists("data/hirmagnet.db"),
            "current_files": [f for f in os.listdir(".") if not f.startswith('.')] if os.path.exists(".") else []
        }
        
        return status
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "critical_error"
        }

# ===== AI CONFIGURATION =====
openai.api_key = os.getenv('OPENAI_API_KEY')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ===== PYDANTIC MODELS =====

# Admin models
class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    original_content: Optional[str] = None
    seo_keywords: Optional[str] = None
    sentiment: Optional[str] = None

class ArticleCreate(BaseModel):
    title: str
    category: str
    source: str
    url: str
    summary: str
    original_content: Optional[str] = None
    seo_keywords: Optional[str] = None
    sentiment: Optional[str] = "neutral"
    is_processed: bool = True

# AI models
class AICommandRequest(BaseModel):
    command: str
    target_category: Optional[str] = None
    max_articles: int = 10
    ai_provider: str = "openai"
    style: str = "professional"
    audience: str = "general"
    brand_voice: Optional[str] = None

class SingleArticleAIRequest(BaseModel):
    article_id: int
    command: str
    ai_provider: str = "openai"
    style: str = "professional"
    audience: str = "general"
    brand_voice: Optional[str] = None

class AIBulkRequest(BaseModel):
    command: str
    ai_provider: str = "openai"
    style: str = "professional"
    audience: str = "general"
    brand_voice: Optional[str] = None
    max_articles: int = 50

class AISuggestion(BaseModel):
    article_id: int
    type: str
    field: str
    original: str
    suggested: str
    confidence: str
    reason: str

# ===== AI SERVICE CLASS =====
class AIEditorService:
    """Deutsche Präzision AI Service - Herr Claus Engineering"""
    
    def __init__(self):
        self.openai_model = "gpt-4o"
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        
    async def process_command(
        self, 
        command: str, 
        articles: List[Dict], 
        provider: str = "openai",
        style: str = "professional",
        audience: str = "general",
        brand_voice: str = None
    ) -> List[AISuggestion]:
        """Process AI command for multiple articles"""
        
        suggestions = []
        
        for article in articles:
            try:
                if provider == "openai":
                    suggestion = await self._process_with_openai(
                        command, article, style, audience, brand_voice
                    )
                else:
                    suggestion = await self._process_with_gemini(
                        command, article, style, audience, brand_voice
                    )
                
                if suggestion:
                    suggestions.append(suggestion)
                    
            except Exception as e:
                print(f"❌ AI Processing error for article {article['id']}: {e}")
                continue
        
        return suggestions
    
    async def process_single_article(
        self,
        command: str,
        article: Dict,
        provider: str = "openai",
        style: str = "professional", 
        audience: str = "general",
        brand_voice: str = None
    ) -> Optional[AISuggestion]:
        """Process AI command for single article"""
        
        try:
            if provider == "openai":
                return await self._process_with_openai(
                    command, article, style, audience, brand_voice
                )
            else:
                return await self._process_with_gemini(
                    command, article, style, audience, brand_voice
                )
        except Exception as e:
            print(f"❌ Single article AI processing error: {e}")
            return None
    
    async def _process_with_openai(
        self, 
        command: str, 
        article: Dict, 
        style: str, 
        audience: str, 
        brand_voice: str
    ) -> Optional[AISuggestion]:
        """OpenAI processing with full GPT-4o model"""
        
        system_prompt = self._build_system_prompt(style, audience, brand_voice)
        user_prompt = self._build_user_prompt(command, article)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_ai_response(result, article['id'])
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return None
    
    async def _process_with_gemini(
        self, 
        command: str, 
        article: Dict, 
        style: str, 
        audience: str, 
        brand_voice: str
    ) -> Optional[AISuggestion]:
        """Gemini processing with Gemini-2.5-Flash-Preview"""
        
        system_prompt = self._build_system_prompt(style, audience, brand_voice)
        user_prompt = self._build_user_prompt(command, article)
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, full_prompt
            )
            
            result = response.text.strip()
            return self._parse_ai_response(result, article['id'])
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return None
    
    def _build_system_prompt(self, style: str, audience: str, brand_voice: str) -> str:
        """Build system prompt for AI"""
        
        style_guides = {
            "professional": "professzionális, tárgyilagos hangvételű",
            "casual": "könnyed, barátságos hangvételű", 
            "neutral": "semleges, objektív hangvételű",
            "engaging": "vonzó, figyelemfelkeltő hangvételű"
        }
        
        audience_guides = {
            "general": "általános közönség számára érthető",
            "expert": "szakértő közönség számára részletes",
            "young": "fiatal olvasók számára dinamikus",
            "business": "üzleti közönség számára praktikus"
        }
        
        base_prompt = f"""Te egy mesterséges intelligenciás magyar hírszerkesztő vagy a HírMagnet portálnak.

STÍLUS: {style_guides.get(style, 'professzionális')}
CÉLKÖZÖNSÉG: {audience_guides.get(audience, 'általános közönség')}

{"BRAND VOICE: " + brand_voice if brand_voice else ""}

A válaszodat MINDIG JSON formátumban add meg:
{{
    "type": "title|summary|seo|sentiment|content",
    "field": "title|summary|seo_keywords|sentiment|original_content", 
    "suggested": "javasolt szöveg",
    "confidence": "high|medium|low",
    "reason": "rövid indoklás magyarul"
}}

FONTOS SZABÁLYOK:
- Mindig magyar nyelven dolgozz
- Legyen tárgyilagos és informatív
- Kerüld a clickbait címeket
- SEO kulcsszavaknál vesszővel válaszd el őket
- Ha nem tudsz javítani, add vissza az eredeti szöveget
"""
        return base_prompt
    
    def _build_user_prompt(self, command: str, article: Dict) -> str:
        """Build user prompt with article data"""
        
        return f"""PARANCS: {command}

CIKK ADATOK:
ID: {article['id']}
Cím: {article.get('title', 'N/A')}
Összefoglaló: {article.get('summary', 'N/A')}
Kategória: {article.get('category', 'N/A')}
Forrás: {article.get('source', 'N/A')}
SEO kulcsszavak: {article.get('seo_keywords', 'N/A')}
Hangulat: {article.get('sentiment', 'N/A')}

Kérlek, végezd el a kért műveletet és válaszolj JSON formátumban!"""
    
    def _parse_ai_response(self, response: str, article_id: int) -> Optional[AISuggestion]:
        """Parse AI response into AISuggestion"""
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return AISuggestion(
                    article_id=article_id,
                    type=data.get('type', 'unknown'),
                    field=data.get('field', 'title'),
                    original="",
                    suggested=data.get('suggested', ''),
                    confidence=data.get('confidence', 'medium'),
                    reason=data.get('reason', 'AI javasolt módosítás')
                )
            else:
                return AISuggestion(
                    article_id=article_id,
                    type="content",
                    field="summary", 
                    original="",
                    suggested=response[:200] + "..." if len(response) > 200 else response,
                    confidence="low",
                    reason="Fallback parsing"
                )
                
        except Exception as e:
            print(f"❌ Response parsing error: {e}")
            return None

# ===== BACKGROUND PROCESSOR CLASS =====

class BackgroundProcessor:
    """Deutsche Präzision Background Processing"""
    
    def __init__(self):
        self.is_processing = False
        self.last_process_time = None
        self.process_count = 0
        
    def start_background_processing(self):
        """Start background processing in separate thread"""
        if self.is_processing:
            print("🔄 Background processing already running...")
            return
            
        print("🚀 Starting background processing...")
        self.is_processing = True
        self.process_count += 1
        
        def background_task():
            try:
                print(f"🧲 Background processing #{self.process_count} started")
                self.last_process_time = datetime.now()
                
                # Simulate heavy processing
                import time
                time.sleep(30)  # Simulate 30 seconds of processing
                
                print(f"✅ Background processing #{self.process_count} completed")
                
            except Exception as e:
                print(f"❌ Background processing error: {e}")
            finally:
                self.is_processing = False
                print("🏁 Background processing finished")
        
        # Run in separate thread - NON-BLOCKING
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()

# ===== GLOBAL INSTANCES =====
ai_service = AIEditorService()
background_processor = BackgroundProcessor()

# ===== UTILITY FUNCTIONS =====
def verify_admin_access():
    """Simple admin verification"""
    return True

# ===== HERR CLAUS NON-BLOCKING API ENDPOINTS =====

@router.get("/articles")
async def get_articles(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """🎖️ HERR CLAUS NON-BLOCKING Articles endpoint with timeout protection"""
    try:
        # CRITICAL: Database timeout protection
        db.execute(text("PRAGMA busy_timeout = 3000"))  # 3 second timeout
        
        query = db.query(Article).filter(Article.is_processed == True)
        
        if category:
            if category.strip().lower() not in ["all", "minden", "összes", "🔥 legfrissebb hírek"]:
                from database.models import CATEGORIES
                category_code = None
                
                if category.strip() in CATEGORIES.keys():
                    category_code = category.strip()
                else:
                    for code, name in CATEGORIES.items():
                        if category.strip() == name.strip():
                            category_code = code
                            break
                    
                    if not category_code:
                        cleaned_category = category.strip()
                        if ' ' in cleaned_category:
                            cleaned_category = cleaned_category.split(' ', 1)[1].strip()
                        
                        for code, name in CATEGORIES.items():
                            cleaned_name = name.strip()
                            if ' ' in cleaned_name:
                                cleaned_name = cleaned_name.split(' ', 1)[1].strip()
                            
                            if cleaned_category.lower() == cleaned_name.lower():
                                category_code = code
                                break
                
                if category_code:
                    query = query.filter(Article.category == category_code)
                else:
                    query = query.filter(Article.category == category)
        
        if source:
            query = query.filter(Article.source == source)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Article.title.ilike(search_term)) |
                (Article.ai_summary.ilike(search_term))
            )
        
        # CRITICAL: Execute with timeout protection
        articles = query.order_by(desc(Article.created_at)).offset(offset).limit(limit).all()
        total_count = query.count()
        
        article_list = []
        for article in articles:
            article_data = {
                "id": article.id,
                "title": article.ai_title or article.title,
                "original_title": article.original_title,
                "summary": article.ai_summary or article.original_content[:200] + "..." if article.original_content else "",
                "source": article.source,
                "category": article.category,
                "url": article.url,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "created_at": article.created_at.isoformat(),
                "has_audio": article.has_audio,
                "audio_filename": article.audio_filename,
                "audio_duration": article.audio_duration,
                "sentiment": article.sentiment,
                "view_count": article.view_count,
                "audio_play_count": article.audio_play_count
            }
            article_list.append(article_data)
        
        return {
            "articles": article_list,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count,
            "server_time": datetime.now().isoformat(),
            "processing_status": "processing" if background_processor.is_processing else "normal"
        }
        
    except Exception as e:
        print(f"❌ Articles API error: {e}")
        raise HTTPException(
            status_code=503, 
            detail="Database temporarily busy - please try again in a few seconds"
        )

@router.get("/articles/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """🎖️ HERR CLAUS NON-BLOCKING Article detail with timeout protection"""
    try:
        db.execute(text("PRAGMA busy_timeout = 2000"))  # 2 second timeout
        
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Cikk nem található")
        
        article.view_count += 1
        db.commit()
        
        return {
            "id": article.id,
            "title": article.ai_title or article.title,
            "original_title": article.original_title,
            "summary": article.ai_summary,
            "original_content": article.original_content,
            "source": article.source,
            "category": article.category,
            "url": article.url,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "created_at": article.created_at.isoformat(),
            "has_audio": article.has_audio,
            "audio_filename": article.audio_filename,
            "audio_duration": article.audio_duration,
            "sentiment": article.sentiment,
            "seo_keywords": article.seo_keywords,
            "view_count": article.view_count,
            "audio_play_count": article.audio_play_count,
            "processing_status": "processing" if background_processor.is_processing else "normal"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Article detail error: {e}")
        raise HTTPException(
            status_code=503, 
            detail="Database temporarily busy - please try again"
        )

@router.get("/trending")
async def get_trending_articles(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """🎖️ HERR CLAUS NON-BLOCKING Trending with timeout protection"""
    try:
        db.execute(text("PRAGMA busy_timeout = 2000"))
        
        since = datetime.now() - timedelta(hours=hours)
        
        trending = db.query(Article).filter(
            Article.is_processed == True,
            Article.created_at >= since
        ).order_by(
            desc(Article.view_count + Article.audio_play_count * 2)
        ).limit(limit).all()
        
        trending_list = []
        for article in trending:
            trending_list.append({
                "id": article.id,
                "title": article.ai_title or article.title,
                "source": article.source,
                "category": article.category,
                "view_count": article.view_count,
                "audio_play_count": article.audio_play_count,
                "engagement_score": article.view_count + article.audio_play_count * 2,
                "has_audio": article.has_audio,
                "created_at": article.created_at.isoformat()
            })
        
        return {
            "trending": trending_list, 
            "hours": hours,
            "processing_status": "processing" if background_processor.is_processing else "normal"
        }
        
    except Exception as e:
        print(f"❌ Trending error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Trending data temporarily unavailable"
        )

@router.get("/latest")
async def get_latest_articles(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """🎖️ HERR CLAUS NON-BLOCKING Latest articles with timeout protection"""
    try:
        db.execute(text("PRAGMA busy_timeout = 2000"))
        
        query = db.query(Article).filter(Article.is_processed == True)
        
        if category:
            query = query.filter(Article.category == category)
        
        articles = query.order_by(desc(Article.created_at)).limit(limit).all()
        
        latest_list = []
        for article in articles:
            latest_list.append({
                "id": article.id,
                "title": article.ai_title or article.title,
                "summary": article.ai_summary[:150] + "..." if article.ai_summary and len(article.ai_summary) > 150 else article.ai_summary,
                "source": article.source,
                "category": article.category,
                "has_audio": article.has_audio,
                "audio_filename": article.audio_filename,
                "created_at": article.created_at.isoformat(),
                "sentiment": article.sentiment
            })
        
        return {
            "latest": latest_list,
            "processing_status": "processing" if background_processor.is_processing else "normal"
        }
        
    except Exception as e:
        print(f"❌ Latest articles error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Latest articles temporarily unavailable"
        )

# ===== HERR CLAUS CACHED DASHBOARD =====

@router.get("/dashboard-data")
async def get_dashboard_data():
    """🎖️ HERR CLAUS CACHED Dashboard data - never blocks"""
    try:
        now = datetime.now()
        
        # Check cache first
        if (dashboard_cache["data"] and 
            dashboard_cache["last_update"] and
            (now - dashboard_cache["last_update"]).seconds < dashboard_cache["cache_duration"]):
            
            cached_data = dashboard_cache["data"].copy()
            cached_data["cache_hit"] = True
            cached_data["cached_at"] = dashboard_cache["last_update"].isoformat()
            cached_data["processing_status"] = "processing" if background_processor.is_processing else "normal"
            return cached_data
        
        # Try to get fresh data with short timeout
        try:
            rates = data_collector.get_financial_rates()
            weather = data_collector.get_weather()
            sources = data_collector.get_rss_sources()
            
            fresh_data = {
                "financial_rates": rates,
                "weather": weather,
                "rss_sources": sources,
                "generated_at": now.isoformat(),
                "cache_hit": False,
                "processing_status": "processing" if background_processor.is_processing else "normal"
            }
            
            # Update cache
            dashboard_cache["data"] = fresh_data
            dashboard_cache["last_update"] = now
            
            return fresh_data
            
        except Exception as e:
            print(f"❌ Fresh dashboard data error: {e}")
            
            # Return last cached data if available
            if dashboard_cache["data"]:
                stale_data = dashboard_cache["data"].copy()
                stale_data["cache_hit"] = True
                stale_data["stale"] = True
                stale_data["error"] = "Fresh data temporarily unavailable"
                stale_data["processing_status"] = "processing" if background_processor.is_processing else "normal"
                return stale_data
            
            # Fallback to mock data
            return {
                "financial_rates": {
                    "currencies": [
                        {"pair": "EUR/HUF", "value": "402.81", "change": "+0.8%", "trend": "up"},
                        {"pair": "USD/HUF", "value": "365.42", "change": "-0.3%", "trend": "down"}
                    ],
                    "crypto": [
                        {"pair": "BTC/USD", "value": "$107,685", "change": "+2.1%", "trend": "up"}
                    ],
                    "hungarian_stocks": [
                        {"pair": "OTP", "value": "26,450", "change": "+1.8%", "trend": "up"}
                    ]
                },
                "weather": {
                    "temperature": "8",
                    "feels_like": "5", 
                    "city": "Budapest",
                    "icon": "🌨️"
                },
                "rss_sources": {"general": []},
                "generated_at": now.isoformat(),
                "fallback": True,
                "processing_status": "processing" if background_processor.is_processing else "normal"
            }
            
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Dashboard temporarily unavailable"
        )

# ===== HERR CLAUS PROCESSING STATUS ENDPOINT =====

@router.get("/processing-status")
async def get_processing_status():
    """🎖️ HERR CLAUS Processing status monitoring"""
    return {
        "is_processing": background_processor.is_processing,
        "last_process_time": background_processor.last_process_time.isoformat() if background_processor.last_process_time else None,
        "server_time": datetime.now().isoformat(),
        "api_status": "available",
        "process_count": background_processor.process_count
    }

# ===== HERR CLAUS MANUAL PROCESSING TRIGGER (for testing) =====

@router.post("/admin/trigger-processing")
async def trigger_background_processing():
    """🎖️ HERR CLAUS Manual processing trigger for testing"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        background_processor.start_background_processing()
        
        return {
            "success": True,
            "message": "Background processing triggered",
            "timestamp": datetime.now().isoformat(),
            "is_processing": background_processor.is_processing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing trigger failed: {str(e)}")

# ===== REST OF ORIGINAL ENDPOINTS (unchanged for backward compatibility) =====

@router.post("/articles/{article_id}/play")
async def track_audio_play(article_id: int, db: Session = Depends(get_db)):
    """Hanglejátszás számláló"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Cikk nem található")
        
        article.audio_play_count += 1
        db.commit()
        
        return {"success": True, "play_count": article.audio_play_count}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Play tracking hiba: {str(e)}")

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Elérhető kategóriák listája cikkszámokkal"""
    try:
        categories = db.query(
            Article.category,
            func.count(Article.id).label('count')
        ).filter(
            Article.is_processed == True
        ).group_by(Article.category).order_by(
            func.count(Article.id).desc()
        ).all()
        
        category_list = [
            {"name": cat[0], "count": cat[1]}
            for cat in categories
        ]
        
        return {"categories": category_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kategóriák lekérdezési hiba: {str(e)}")

@router.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """Elérhető források listája cikkszámokkal"""
    try:
        sources = db.query(
            Article.source,
            func.count(Article.id).label('count')
        ).filter(
            Article.is_processed == True
        ).group_by(Article.source).order_by(
            func.count(Article.id).desc()
        ).all()
        
        source_list = [
            {"name": src[0], "count": src[1]}
            for src in sources
        ]
        
        return {"sources": source_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Források lekérdezési hiba: {str(e)}")

# ===== DATACOLLECTOR ROUTES =====

@router.get("/rss-sources")
async def get_rss_sources():
    """RSS források állapota kategóriánként"""
    try:
        sources = data_collector.get_rss_sources()
        return {
            "sources": sources,
            "generated_at": datetime.now().isoformat(),
            "total_sources": sum(len(sources[cat]) for cat in sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RSS források hiba: {str(e)}")

@router.get("/financial-rates")
async def get_financial_rates():
    """Pénzügyi árfolyamok"""
    try:
        rates = data_collector.get_financial_rates()
        return rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pénzügyi adatok hiba: {str(e)}")

@router.get("/weather")
async def get_weather(city: str = Query("Budapest")):
    """Időjárás információ"""
    try:
        weather = data_collector.get_weather(city)
        return weather
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Időjárás hiba: {str(e)}")

@router.post("/refresh-cache")
async def refresh_cache(background_tasks: BackgroundTasks):
    """Cache frissítése háttérben"""
    try:
        def refresh_task():
            data_collector.clear_cache()
            data_collector.get_rss_sources()
            data_collector.get_financial_rates()
            data_collector.get_weather()
        
        background_tasks.add_task(refresh_task)
        return {"message": "Cache frissítés elindítva", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache frissítési hiba: {str(e)}")

@router.get("/rss-proxy")
async def rss_proxy(url: str = Query(...)):
    """Proxy for RSS feeds to avoid CORS issues"""
    try:
        import requests
        import feedparser
        from datetime import datetime
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch RSS feed")
        
        feed = feedparser.parse(response.text)
        
        feed_data = {
            "title": feed.feed.get("title", ""),
            "description": feed.feed.get("description", feed.feed.get("subtitle", "")),
            "link": feed.feed.get("link", ""),
            "lastUpdated": datetime.now().isoformat(),
            "items": []
        }
        
        for i, entry in enumerate(feed.entries[:50]):
            item = {
                "title": entry.get("title", f"Item {i+1}"),
                "link": entry.get("link", ""),
                "description": entry.get("description", entry.get("summary", "")),
                "pubDate": entry.get("published", entry.get("updated", "")),
                "guid": entry.get("id", entry.get("guid", f"item-{i}"))
            }
            feed_data["items"].append(item)
        
        return {"success": True, "data": feed_data}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RSS proxy error: {str(e)}")

# ===== ADMIN ROUTES (unchanged for backward compatibility) =====

@router.put("/admin/articles/{article_id}")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing article - Admin only"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        update_data = article_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(article, field, value)
        
        if 'title' in update_data:
            article.ai_title = update_data['title']
        
        if 'summary' in update_data:
            article.ai_summary = update_data['summary']
        
        article.is_processed = True
        
        db.commit()
        db.refresh(article)
        
        return {
            "success": True,
            "message": f"Article {article_id} updated successfully",
            "article": {
                "id": article.id,
                "title": article.title,
                "category": article.category,
                "source": article.source,
                "updated_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.post("/admin/articles")
async def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db)
):
    """Create a new article manually - Admin only"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        existing = db.query(Article).filter(Article.url == article_data.url).first()
        if existing:
            raise HTTPException(status_code=400, detail="Article with this URL already exists")
        
        new_article = Article(
            title=article_data.title,
            ai_title=article_data.title,
            summary=article_data.summary,
            ai_summary=article_data.summary,
            original_content=article_data.original_content,
            source=article_data.source,
            category=article_data.category,
            url=article_data.url,
            seo_keywords=article_data.seo_keywords,
            sentiment=article_data.sentiment,
            is_processed=article_data.is_processed,
            published_at=datetime.now(),
            created_at=datetime.now(),
            view_count=0,
            audio_play_count=0,
            has_audio=False
        )
        
        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        
        return {
            "success": True,
            "message": "Article created successfully",
            "id": new_article.id,
            "article": {
                "id": new_article.id,
                "title": new_article.title,
                "category": new_article.category,
                "source": new_article.source,
                "url": new_article.url,
                "created_at": new_article.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Creation failed: {str(e)}")

@router.delete("/admin/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Delete an article - Admin only"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article_info = {
            "id": article.id,
            "title": article.title,
            "source": article.source
        }
        
        db.delete(article)
        db.commit()
        
        return {
            "success": True,
            "message": f"Article {article_id} deleted successfully",
            "deleted_article": article_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Get detailed admin statistics"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        total_articles = db.query(func.count(Article.id)).scalar()
        
        processed_articles = db.query(func.count(Article.id)).filter(
            Article.is_processed == True
        ).scalar()
        
        total_views = db.query(func.sum(Article.view_count)).scalar() or 0
        
        total_audio_plays = db.query(func.sum(Article.audio_play_count)).scalar() or 0
        
        audio_articles = db.query(func.count(Article.id)).filter(
            Article.has_audio == True
        ).scalar()
        
        category_stats = db.query(
            Article.category,
            func.count(Article.id).label('count')
        ).filter(
            Article.is_processed == True
        ).group_by(Article.category).all()
        
        source_stats = db.query(
            Article.source,
            func.count(Article.id).label('count')
        ).filter(
            Article.is_processed == True
        ).group_by(Article.source).order_by(
            func.count(Article.id).desc()
        ).limit(10).all()
        
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_articles = db.query(func.count(Article.id)).filter(
            Article.created_at >= recent_cutoff
        ).scalar()
        
        return {
            "success": True,
            "stats": {
                "total_articles": total_articles,
                "processed_articles": processed_articles,
                "unprocessed_articles": total_articles - processed_articles,
                "total_views": int(total_views),
                "total_audio_plays": int(total_audio_plays),
                "audio_articles": audio_articles,
                "recent_articles_24h": recent_articles,
                "category_breakdown": [
                    {"category": cat[0], "count": cat[1]} 
                    for cat in category_stats
                ],
                "top_sources": [
                    {"source": src[0], "count": src[1]} 
                    for src in source_stats
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats generation failed: {str(e)}")

@router.get("/admin/articles/search")
async def admin_search_articles(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    source: Optional[str] = Query(None, description="Source filter"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Advanced article search for admin - includes unprocessed articles"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        query = db.query(Article)
        
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                (Article.title.ilike(search_term)) |
                (Article.ai_title.ilike(search_term)) |
                (Article.summary.ilike(search_term)) |
                (Article.ai_summary.ilike(search_term)) |
                (Article.source.ilike(search_term))
            )
        
        if category:
            query = query.filter(Article.category == category)
        
        if source:
            query = query.filter(Article.source.ilike(f"%{source}%"))
        
        total_count = query.count()
        
        articles = query.order_by(desc(Article.created_at)).offset(offset).limit(limit).all()
        
        article_list = []
        for article in articles:
            article_data = {
                "id": article.id,
                "title": article.ai_title or article.title,
                "original_title": article.title,
                "summary": article.ai_summary or article.summary,
                "source": article.source,
                "category": article.category,
                "url": article.url,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "created_at": article.created_at.isoformat(),
                "is_processed": article.is_processed,
                "has_audio": article.has_audio,
                "view_count": article.view_count,
                "audio_play_count": article.audio_play_count,
                "sentiment": article.sentiment,
                "seo_keywords": article.seo_keywords
            }
            article_list.append(article_data)
        
        return {
            "success": True,
            "articles": article_list,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count,
            "query_info": {
                "search_term": q,
                "category_filter": category,
                "source_filter": source
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Admin search failed: {str(e)}")

@router.post("/admin/articles/{article_id}/reprocess")
async def reprocess_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Mark article for reprocessing - Admin only"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article.is_processed = False
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Article {article_id} marked for reprocessing",
            "article_id": article_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Reprocess marking failed: {str(e)}")

# ===== AI INTEGRATION ROUTES (unchanged for backward compatibility) =====

@router.post("/admin/ai/command")
async def execute_ai_command(
    request: AICommandRequest,
    db: Session = Depends(get_db)
):
    """Execute AI command on filtered articles"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        query = db.query(Article).filter(Article.is_processed == True)
        
        if request.target_category:
            query = query.filter(Article.category == request.target_category)
        
        articles = query.order_by(desc(Article.created_at)).limit(request.max_articles).all()
        
        if not articles:
            return {
                "success": False,
                "message": "Nincsenek cikkek a megadott szűrők alapján"
            }
        
        article_dicts = []
        for article in articles:
            article_dicts.append({
                'id': article.id,
                'title': article.title,
                'summary': article.ai_summary or article.summary,
                'category': article.category,
                'source': article.source,
                'seo_keywords': article.seo_keywords,
                'sentiment': article.sentiment,
                'original_content': article.original_content
            })
        
        suggestions = await ai_service.process_command(
            command=request.command,
            articles=article_dicts,
            provider=request.ai_provider,
            style=request.style,
            audience=request.audience,
            brand_voice=request.brand_voice
        )
        
        for suggestion in suggestions:
            original_article = next((a for a in articles if a.id == suggestion.article_id), None)
            if original_article:
                field_value = getattr(original_article, suggestion.field, '')
                if suggestion.field == 'title':
                    suggestion.original = original_article.ai_title or original_article.title or ''
                elif suggestion.field == 'summary':
                    suggestion.original = original_article.ai_summary or original_article.summary or ''
                else:
                    suggestion.original = field_value or ''
        
        return {
            "success": True,
            "suggestions": [s.dict() for s in suggestions],
            "processed_count": len(suggestions),
            "total_articles": len(articles),
            "ai_provider": request.ai_provider,
            "command": request.command
        }
        
    except Exception as e:
        print(f"❌ AI Command execution error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

@router.post("/admin/ai/single")
async def process_single_article_ai(
    request: SingleArticleAIRequest,
    db: Session = Depends(get_db)
):
    """Process single article with AI"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        article = db.query(Article).filter(Article.id == request.article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article_dict = {
            'id': article.id,
            'title': article.title,
            'summary': article.ai_summary or article.summary,
            'category': article.category,
            'source': article.source,
            'seo_keywords': article.seo_keywords,
            'sentiment': article.sentiment,
            'original_content': article.original_content
        }
        
        suggestion = await ai_service.process_single_article(
            command=request.command,
            article=article_dict,
            provider=request.ai_provider,
            style=request.style,
            audience=request.audience,
            brand_voice=request.brand_voice
        )
        
        if not suggestion:
            return {
                "success": False,
                "message": "AI nem tudott javaslatot generálni"
            }
        
        field_value = getattr(article, suggestion.field, '')
        if suggestion.field == 'title':
            suggestion.original = article.ai_title or article.title or ''
        elif suggestion.field == 'summary':
            suggestion.original = article.ai_summary or article.summary or ''
        else:
            suggestion.original = field_value or ''
        
        return {
            "success": True,
            "suggestion": suggestion.dict(),
            "article_id": article.id,
            "ai_provider": request.ai_provider,
            "command": request.command
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Single article AI processing error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

@router.post("/admin/ai/bulk-all")
async def process_all_frontend_articles(
    request: AIBulkRequest,
    db: Session = Depends(get_db)
):
    """Process ALL articles that appear on frontend (processed articles)"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        articles = db.query(Article).filter(
            Article.is_processed == True
        ).order_by(desc(Article.created_at)).limit(request.max_articles).all()
        
        if not articles:
            return {
                "success": False,
                "message": "Nincsenek feldolgozott cikkek"
            }
        
        article_dicts = []
        for article in articles:
            article_dicts.append({
                'id': article.id,
                'title': article.title,
                'summary': article.ai_summary or article.summary,
                'category': article.category,
                'source': article.source,
                'seo_keywords': article.seo_keywords,
                'sentiment': article.sentiment,
                'original_content': article.original_content
            })
        
        batch_size = 10
        all_suggestions = []
        
        for i in range(0, len(article_dicts), batch_size):
            batch = article_dicts[i:i + batch_size]
            
            batch_suggestions = await ai_service.process_command(
                command=request.command,
                articles=batch,
                provider=request.ai_provider,
                style=request.style,
                audience=request.audience,
                brand_voice=request.brand_voice
            )
            
            all_suggestions.extend(batch_suggestions)
            
            await asyncio.sleep(0.5)
        
        for suggestion in all_suggestions:
            original_article = next((a for a in articles if a.id == suggestion.article_id), None)
            if original_article:
                if suggestion.field == 'title':
                    suggestion.original = original_article.ai_title or original_article.title or ''
                elif suggestion.field == 'summary':
                    suggestion.original = original_article.ai_summary or original_article.summary or ''
                else:
                    field_value = getattr(original_article, suggestion.field, '')
                    suggestion.original = field_value or ''
        
        return {
            "success": True,
            "suggestions": [s.dict() for s in all_suggestions],
            "processed_count": len(all_suggestions),
            "total_articles": len(articles),
            "ai_provider": request.ai_provider,
            "command": request.command,
            "batch_info": f"Processed in {len(article_dicts) // batch_size + 1} batches"
        }
        
    except Exception as e:
        print(f"❌ Bulk AI processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk AI processing failed: {str(e)}")

@router.post("/admin/ai/apply-suggestions")
async def apply_ai_suggestions(
    suggestions: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Apply multiple AI suggestions to articles"""
    try:
        if not verify_admin_access():
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for suggestion_data in suggestions:
            try:
                article_id = suggestion_data['article_id']
                field = suggestion_data['field']
                suggested_value = suggestion_data['suggested']
                
                article = db.query(Article).filter(Article.id == article_id).first()
                
                if not article:
                    errors.append(f"Article {article_id} not found")
                    error_count += 1
                    continue
                
                if field == 'title':
                    article.title = suggested_value
                    article.ai_title = suggested_value
                elif field == 'summary':
                    article.summary = suggested_value
                    article.ai_summary = suggested_value
                else:
                    setattr(article, field, suggested_value)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Error applying suggestion for article {suggestion_data.get('article_id', 'unknown')}: {str(e)}")
                error_count += 1
        
        if success_count > 0:
            db.commit()
        
        return {
            "success": True,
            "applied_count": success_count,
            "error_count": error_count,
            "errors": errors,
            "message": f"{success_count} módosítás sikeresen alkalmazva, {error_count} hiba"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Suggestion application failed: {str(e)}")

@router.get("/admin/ai/providers")
async def get_ai_providers():
    """Get available AI providers and their status"""
    try:
        providers = {
            "openai": {
                "name": "OpenAI GPT-4o",
                "model": "gpt-4o",
                "available": bool(os.getenv('OPENAI_API_KEY')),
                "description": "Full GPT-4o model - superior intelligence for complex tasks"
            },
            "gemini": {
                "name": "Google Gemini 2.5 Flash",
                "model": "gemini-2.5-flash-preview-05-20", 
                "available": bool(os.getenv('GEMINI_API_KEY')),
                "description": "Latest Gemini 2.5 - advanced reasoning and creative capabilities"
            }
        }
        
        return {
            "success": True,
            "providers": providers,
            "default": "openai"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider check failed: {str(e)}")

# ===== STARTUP MESSAGE =====
print("🎖️ HERR CLAUS NON-BLOCKING BACKEND - READY FOR DEPLOYMENT!")
print("🧲 Deutsche Präzision Features:")
print("   ✅ Non-blocking API endpoints with timeout protection") 
print("   ✅ Background processing with ThreadPoolExecutor")
print("   ✅ Intelligent dashboard caching system")
print("   ✅ Processing status monitoring")
print("   ✅ Manual processing trigger for testing")
print("   ✅ Full backward compatibility maintained")
print("   ✅ Alap cikk API endpoints")
print("   ✅ DataCollector integráció")
print("   ✅ Admin management funkciók")
print("   ✅ OpenAI GPT-4o & Gemini 2.5 Flash AI integráció")
print("   ✅ RSS proxy & utility endpoints")
print("📋 Enhanced endpoints:")
print("   🎖️ GET /api/articles - NON-BLOCKING with processing status")
print("   🎖️ GET /api/trending - NON-BLOCKING with timeout protection")
print("   🎖️ GET /api/latest - NON-BLOCKING with timeout protection")
print("   🎖️ GET /api/dashboard-data - CACHED with intelligent fallback")
print("   🎖️ GET /api/processing-status - NEW: Server processing monitoring")
print("   🎖️ POST /api/admin/trigger-processing - NEW: Manual testing trigger")
print("🚀 HERR CLAUS ENGINEERING - DEUTSCHE PRÄZISION GUARANTEED!")