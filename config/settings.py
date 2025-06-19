import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

# Database
DATABASE_URL = "sqlite:///./data/hirmagnet.db"

# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# AI Settings
MAX_SUMMARY_LENGTH = 1500  # JAVÍTOTT - hosszú cikkekhez
TTS_VOICE = "alloy"  # OpenAI TTS hangok: alloy, echo, fable, onyx, nova, shimmer
TTS_SPEED = 1.0

# Scraping settings
SCRAPE_INTERVAL_MINUTES = 60
MAX_ARTICLES_PER_SOURCE = 10
REQUEST_TIMEOUT = 10

# Audio settings
AUDIO_DIR = "./static/audio"
AUDIO_FORMAT = "mp3"

# Cache settings
CACHE_ARTICLES_HOURS = 24

# Google AdSense (később beállítod)
ADSENSE_CLIENT_ID = "ca-pub-your-adsense-id"
ADSENSE_SLOT_ID = "your-ad-slot-id"

# Site settings
SITE_NAME = "HírMagnet"
SITE_DESCRIPTION = "AI-alapú magyar hírportál hangfelolvasással"
SITE_URL = "https://your-domain.hu"

# Hosszú cikk beállítások
AI_MAX_TOKENS = 1800
AI_ARTICLE_TARGET_LENGTH = 1200
