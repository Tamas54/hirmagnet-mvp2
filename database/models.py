# database/models.py - ENHANCED VERSION WITH AI JOURNALIST SUPPORT
# ACHTUNG! BACKWARD COMPATIBILITY MAINTAINED!

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class User(Base):
    """User modell Premium előfizetésekkel"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=True)
    is_premium = Column(Boolean, default=False)
    premium_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # User preferences
    preferred_categories = Column(String(500), nullable=True)  # JSON string
    audio_speed = Column(Float, default=1.0)
    newsletter_subscribed = Column(Boolean, default=True)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")

class Subscription(Base):
    """Stripe előfizetések"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False)  # active, cancelled, past_due
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    original_title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    original_content = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # AI feldolgozás
    is_processed = Column(Boolean, default=False)
    ai_summary = Column(Text, nullable=True)
    ai_title = Column(String(500), nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    
    # ⚡ ENHANCED: 20-POINT IMPORTANCE SCALE
    importance_score = Column(Float, default=0.0)  # 1-20 fontossági skála
    
    # 👥 NEW: AI JOURNALIST SUPPORT
    assigned_journalist = Column(String(100), nullable=True)  # journalist_id (pl: "analitikus_alfonz")
    journalist_name = Column(String(200), nullable=True)      # human readable name  
    processing_model = Column(String(50), nullable=True)      # "gpt4o", "gemini", "hybrid"
    processing_notes = Column(Text, nullable=True)            # Additional processing info
    
    # Audio
    has_audio = Column(Boolean, default=False)
    audio_filename = Column(String(200), nullable=True)
    audio_duration = Column(Float, nullable=True)
    
    # Engagement
    view_count = Column(Integer, default=0)
    audio_play_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # SEO & Social
    seo_keywords = Column(String(500), nullable=True)
    click_count = Column(Integer, default=0)
    social_score = Column(Float, default=0.0)  # Twitter engagement score
    
    # Content flags
    is_breaking = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

class SocialPost(Base):
    """Social media kimenetekhez"""
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # twitter, spotify, youtube
    content_type = Column(String(50), nullable=False)  # thread, podcast, video
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    
    # Platform specific IDs
    twitter_thread_id = Column(String(100), nullable=True)
    spotify_episode_id = Column(String(100), nullable=True)
    youtube_video_id = Column(String(100), nullable=True)
    
    # Statistics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Associated articles
    article_ids = Column(Text, nullable=True)  # JSON array of article IDs
    
    created_at = Column(DateTime, default=func.now())
    published_at = Column(DateTime, nullable=True)
    status = Column(String(50), default='draft')  # draft, published, failed

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    action = Column(String(100), nullable=False)  # Enhanced action types
    source = Column(String(100), nullable=True)
    articles_processed = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)  # Enhanced stats storage
    processing_time = Column(Float, nullable=True)  # seconds
    
    # Social media specific logs
    platform = Column(String(50), nullable=True)
    posts_created = Column(Integer, default=0)

class SiteStats(Base):
    __tablename__ = "site_stats"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=func.now())
    total_articles = Column(Integer, default=0)
    daily_views = Column(Integer, default=0)
    daily_audio_plays = Column(Integer, default=0)
    premium_users = Column(Integer, default=0)
    top_category = Column(String(50), nullable=True)
    avg_time_on_site = Column(Float, nullable=True)
    unique_visitors = Column(Integer, default=0)
    
    # Social metrics
    twitter_followers = Column(Integer, default=0)
    spotify_subscribers = Column(Integer, default=0)
    youtube_subscribers = Column(Integer, default=0)
    
    # ⚡ ENHANCED: AI PROCESSING STATISTICS
    daily_gemini_usage = Column(Integer, default=0)  # Napi Gemini használat
    daily_gpt4o_usage = Column(Integer, default=0)   # Napi GPT-4o használat
    daily_ai_cost = Column(Float, default=0.0)       # Becsült napi AI költség
    
    # 👥 NEW: JOURNALIST STATISTICS
    daily_journalist_usage = Column(Text, nullable=True)  # JSON journalist usage stats

# 👥 NEW: AI JOURNALIST TRACKING TABLE
class AIJournalistStats(Base):
    """AI Újságíró teljesítmény nyomon követése"""
    __tablename__ = "ai_journalist_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.now())
    journalist_id = Column(String(100), nullable=False, index=True)  # "analitikus_alfonz"
    journalist_name = Column(String(200), nullable=False)            # "Analitikus Alfonz"
    
    # Daily stats
    articles_written = Column(Integer, default=0)
    avg_importance_score = Column(Float, default=0.0)
    total_views = Column(Integer, default=0)
    total_audio_plays = Column(Integer, default=0)
    
    # Quality metrics
    avg_sentiment_accuracy = Column(Float, default=0.0)
    keyword_relevance_score = Column(Float, default=0.0)
    
    # Model usage
    gpt4o_articles = Column(Integer, default=0)
    gemini_articles = Column(Integer, default=0)
    
    # Categories covered
    categories_covered = Column(String(500), nullable=True)  # JSON list

# Kategóriák konstansok - ENHANCED
CATEGORIES = {
    "general": "📰 Általános",
    "politics": "🏛️ Politika", 
    "economy": "📈 Gazdaság",
    "tech": "💻 Tech & Tudomány",
    "entertainment": "🎭 Bulvár & Szórakozás",
    "sport": "⚽ Sport",
    "foreign": "🌍 Külföld",
    "health": "🏥 Egészség",
    "lifestyle": "✨ Életmód",
    "cars": "🚗 Autók"
}

# ⚡ ENHANCED: 20-POINT IMPORTANCE SCALE
IMPORTANCE_LEVELS = {
    20: "🚨 WORLD BREAKING - Világválság",
    19: "🔥 NATIONAL BREAKING - Nemzeti válság", 
    18: "⚡ CRITICAL EVENT - Kritikus esemény",
    17: "📢 MAJOR NEWS - Nagy fontosságú",
    16: "📰 IMPORTANT - Fontos hír",
    15: "🎯 SIGNIFICANT - Jelentős",
    14: "📝 NOTABLE - Figyelemre méltó",
    13: "📊 STANDARD HIGH - Standard magas",
    12: "📄 STANDARD - Standard",
    11: "📋 REGULAR - Szokásos",
    10: "📌 MEDIUM - Közepes",
    9: "💬 DISCUSSION - Beszédtéma",
    8: "📋 ROUTINE - Rutin",
    7: "📄 MINOR - Kisebb",
    6: "💤 LOW PRIORITY - Alacsony prioritás",
    5: "📰 FILLER - Kitöltő",
    4: "📋 TRIVIAL - Triviális",
    3: "💭 CASUAL - Alkalmi",
    2: "📌 MINIMAL - Minimális",
    1: "🗑️ IRRELEVANT - Irreleváns"
}

# 👥 AI JOURNALIST DEFINITIONS
AI_JOURNALISTS = {
    "analitikus_alfonz": {
        "name": "Analitikus Alfonz",
        "icon": "🎓",
        "specialty": ["politics", "society", "analysis"],
        "style": "Mélyelemző politikai és társadalmi szakértő",
        "preferred_model": "gpt4o",
        "tier": "premium"
    },
    "elemzo_egon": {
        "name": "Elemző Egon",
        "icon": "📊", 
        "specialty": ["economy", "finance", "markets"],
        "style": "Gazdasági és piaci mélyelemző",
        "preferred_model": "gpt4o",
        "tier": "premium"
    },
    "technologiai_tamas": {
        "name": "Technológiai Tamás",
        "icon": "💻",
        "specialty": ["tech", "science", "innovation"],
        "style": "Tech innovációs guru",
        "preferred_model": "hybrid",
        "tier": "expert"
    },
    "gazdasagi_geza": {
        "name": "Gazdasági Géza",
        "icon": "💰",
        "specialty": ["economy", "business", "startups"],
        "style": "Üzleti és startup szakértő",
        "preferred_model": "hybrid", 
        "tier": "expert"
    },
    "kivancsai_karola": {
        "name": "Kíváncsi Karola",
        "icon": "✨",
        "specialty": ["entertainment", "lifestyle", "celebrity"],
        "style": "Bulvár és lifestyle specialista",
        "preferred_model": "gemini",
        "tier": "standard"
    },
    "sportos_sara": {
        "name": "Sportos Sára",
        "icon": "⚽",
        "specialty": ["sport", "fitness", "competition"],
        "style": "Sport és verseny szakértő",
        "preferred_model": "gemini",
        "tier": "standard"
    },
    "autos_aladar": {
        "name": "Autós Aladár",
        "icon": "🚗",
        "specialty": ["cars", "automotive", "racing"],
        "style": "Autós és motorsport szakértő",
        "preferred_model": "gemini",
        "tier": "standard"
    }
}

# MODEL ROUTING CONFIG - ENHANCED
PREMIUM_THRESHOLD = 17         # GPT-4o automatic threshold (20-point scale)
QUOTA_THRESHOLD = 15          # GPT-4o with quota threshold  
DAILY_PREMIUM_LIMIT = 10      # Max daily premium articles (increased)

# JOURNALIST ROUTING THRESHOLDS
JOURNALIST_THRESHOLDS = {
    "premium_analysts": 15,    # Minimum importance for premium analysts
    "hybrid_experts": 12,      # Minimum importance for hybrid experts  
    "gemini_team": 5          # Minimum importance for Gemini team
}

# PROCESSING ACTION TYPES - ENHANCED
PROCESSING_ACTIONS = [
    "scraping",
    "ai_processing", 
    "dual_phase_ai_processing",
    "integrated_dual_phase_ai_v3",  # NEW
    "tts_generation",
    "social_posting",
    "editorial_processing",          # NEW
    "journalist_assignment",         # NEW
    "cleanup"
]

# BACKWARD COMPATIBILITY HELPERS
def get_legacy_importance_score(twenty_point_score):
    """Convert 20-point scale to legacy 10-point scale"""
    return min(10, max(1, int((twenty_point_score / 20) * 10)))

def get_enhanced_importance_score(ten_point_score):
    """Convert legacy 10-point scale to 20-point scale"""
    return min(20, max(1, int((ten_point_score / 10) * 20)))

def is_journalist_available(journalist_id):
    """Check if journalist is available and properly configured"""
    return journalist_id in AI_JOURNALISTS

def get_journalist_info(journalist_id):
    """Get journalist information by ID"""
    return AI_JOURNALISTS.get(journalist_id, {
        "name": "Unknown Journalist",
        "icon": "❓",
        "specialty": ["general"],
        "style": "Generic reporter",
        "preferred_model": "gemini",
        "tier": "standard"
    })

# DATABASE MIGRATION HELPERS (for existing installations)
def add_journalist_columns_if_missing():
    """
    Helper function to add new journalist columns to existing databases
    Call this during upgrade process
    """
    try:
        from sqlalchemy import text
        from database.db import engine
        
        # Check if new columns exist, add if missing
        alter_statements = [
            "ALTER TABLE articles ADD COLUMN assigned_journalist VARCHAR(100)",
            "ALTER TABLE articles ADD COLUMN journalist_name VARCHAR(200)",
            "ALTER TABLE articles ADD COLUMN processing_model VARCHAR(50)",
            "ALTER TABLE articles ADD COLUMN processing_notes TEXT"
        ]
        
        with engine.connect() as conn:
            for statement in alter_statements:
                try:
                    conn.execute(text(statement))
                    print(f"✅ Added column: {statement}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️ Column already exists: {statement}")
                    else:
                        print(f"❌ Failed to add column: {statement} - {e}")
        
        print("🔄 Journalist columns migration complete")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")

# VALIDATION FUNCTIONS
def validate_importance_score(score):
    """Validate and clamp importance score to 1-20 range"""
    if score is None:
        return 8  # Default middle value
    return max(1, min(20, int(score)))

def validate_journalist_assignment(journalist_id, category, importance_score):
    """Validate journalist assignment makes sense"""
    if not journalist_id or journalist_id not in AI_JOURNALISTS:
        return False
    
    journalist_info = AI_JOURNALISTS[journalist_id]
    
    # Check category match
    if category not in journalist_info["specialty"]:
        return False
    
    # Check importance threshold
    tier = journalist_info["tier"]
    min_importance = JOURNALIST_THRESHOLDS.get(f"{tier}_analysts", 
                                              JOURNALIST_THRESHOLDS.get(f"{tier}_experts",
                                                                       JOURNALIST_THRESHOLDS.get("gemini_team", 5)))
    
    return importance_score >= min_importance

# STATS CALCULATION HELPERS
def calculate_journalist_performance_score(journalist_id, timeframe_days=30):
    """Calculate performance score for journalist"""
    # This would be implemented with actual database queries
    # Returns score 0-100 based on views, engagement, accuracy
    return 85.0  # Placeholder

def get_category_distribution(limit_days=7):
    """Get category distribution for recent articles"""
    # This would be implemented with actual database queries
    return {
        "politics": 25,
        "economy": 20,
        "tech": 15,
        "sport": 12,
        "entertainment": 10,
        "foreign": 8,
        "lifestyle": 6,
        "cars": 3,
        "health": 1
    }

# SYSTEM HEALTH CHECKS
def validate_system_health():
    """Validate system health for AI processing"""
    health_status = {
        "database": True,
        "prompt_manager": PROMPT_MANAGER_AVAILABLE if 'PROMPT_MANAGER_AVAILABLE' in globals() else False,
        "journalist_manager": True,  # Assume available if models loaded
        "ai_models": True,  # Check would be implemented
        "disk_space": True,  # Check would be implemented
        "api_quotas": True   # Check would be implemented
    }
    
    return health_status

print("🧲 Enhanced Models loaded with AI Journalist support!")
print(f"👥 Available journalists: {len(AI_JOURNALISTS)}")
print(f"📊 20-point importance scale: ACTIVE")
print(f"🔄 Backward compatibility: MAINTAINED")
