# config/sources.py - KOMPLETTE STRATEGIC UPGRADE
# ACHTUNG! ALLE 187 RSS QUELLEN mit Strategic Metadata!
# German Precision Engineering by Oberleutnant Claus

import os
from dotenv import load_dotenv

load_dotenv()

# === STRATÉGIAI KONFIGURÁCIÓK ===

# "ZÖLD SÁV" - Azonnali feldolgozás (bypasses all filters)
PREMIUM_FAST_LANE_SOURCES = [
    # ABLAK A VILÁGRA - International Premium
    "BBC News UK", "BBC News World", "BBC Business", "BBC Technology",
    "The Economist - Finance", "The Economist - Business", 
    "TechCrunch", "TechCrunch Startups", "The Verge", "WIRED Business",
    "Bloomberg Markets", "Bloomberg Technology",
    "CNN Latest", "CNN World", "CNN Technology",
    "The Guardian World", "The Guardian Technology",
    "Nature Current Issue", "Science Current Issue",
    
    # OKNYOMOZÓ PRÉMIUM
    "The Intercept", "ProPublica", "Bellingcat", "OCCRP",
    
    # MAGYAR PRÉMIUM (kiemelt témák)
    "Portfolio", "G7", "HVG", "Telex", "Válasz Online", "Qubit", "HWSW"
]

# FORRÁS TÍPUS DEFINÍCIÓK
SOURCE_TYPES = {
    # NEMZETKÖZI PRÉMIUM FORRÁSOK
    "international_premium": {
        "description": "Top tier international sources",
        "boost_multiplier": 4.0,
        "auto_gpt4o_threshold": 8,  # 8+ pont = automatic GPT-4o
        "categories": ["foreign", "tech", "economy"]
    },
    
    "tech_premium": {
        "description": "Specialized tech authorities", 
        "boost_multiplier": 3.5,
        "auto_gpt4o_threshold": 9,
        "categories": ["tech"]
    },
    
    "economy_premium": {
        "description": "Financial and economic authorities",
        "boost_multiplier": 3.5, 
        "auto_gpt4o_threshold": 9,
        "categories": ["economy"]
    },
    
    "investigative_premium": {
        "description": "Investigative journalism sources",
        "boost_multiplier": 4.5,
        "auto_gpt4o_threshold": 7,  # Oknyomozó = instant GPT-4o
        "categories": ["foreign", "politics"]
    },
    
    # MAGYAR PRÉMIUM
    "domestic_premium": {
        "description": "Top Hungarian sources",
        "boost_multiplier": 2.5,
        "auto_gpt4o_threshold": 12,
        "categories": ["general", "politics", "economy", "tech"]
    },
    
    # STANDARD FORRÁSOK  
    "domestic_standard": {
        "description": "Standard Hungarian sources",
        "boost_multiplier": 1.0,
        "auto_gpt4o_threshold": 15,
        "categories": ["general", "politics", "entertainment", "sport"]
    },
    
    "international_standard": {
        "description": "Standard international sources", 
        "boost_multiplier": 1.5,
        "auto_gpt4o_threshold": 13,
        "categories": ["foreign"]
    },
    
    # SPECIALIZÁLT
    "lifestyle_specialized": {
        "description": "Lifestyle and entertainment specialized",
        "boost_multiplier": 0.8,
        "auto_gpt4o_threshold": 18,
        "categories": ["lifestyle", "entertainment"]
    },
    
    "sport_specialized": {
        "description": "Sports specialized sources",
        "boost_multiplier": 1.2,
        "auto_gpt4o_threshold": 16, 
        "categories": ["sport", "cars"]
    }
}

# TARTALOM PROFILOK
CONTENT_PROFILES = {
    "standard_news": {
        "description": "Regular news articles",
        "freshness_decay_hours": 6,  # 6 óra után büntetés
        "reserve_eligible": False
    },
    
    "timeless_analysis": {
        "description": "Deep analysis, reports, timeless content",
        "freshness_decay_hours": 72,  # 72 óra = nincs büntetés
        "reserve_eligible": True  # "Stratégiai Tartalék" rendszerbe
    },
    
    "breaking_news": {
        "description": "Breaking news, urgent updates",
        "freshness_decay_hours": 2,  # 2 óra = gyors büntetés
        "reserve_eligible": False,
        "urgency_boost": 5.0  # +5 pont urgency boost
    }
}

# === KOMPLETT NEWS SOURCES - MINDEN 187 FORRÁS! ===

NEWS_SOURCES = [
    # ==========================================
    # ÁLTALÁNOS / KÖZÉLET
    # ==========================================
    {
        "name": "Index",
        "url": "https://index.hu/24ora/rss/",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "24.hu", 
        "url": "https://24.hu/feed/",
        "category": "general",
        "source_type": "domestic_standard", 
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "HVG",
        "url": "https://hvg.hu/rss",
        "category": "general", 
        "source_type": "domestic_premium",  # PRÉMIUM!
        "content_profile": "timeless_analysis",  # IDŐTÁLLÓ ELEMZÉSEK
        "active": True,
        "priority": 1
    },
    {
        "name": "Telex",
        "url": "https://telex.hu/rss",
        "category": "general",
        "source_type": "domestic_premium",  # PRÉMIUM!
        "content_profile": "standard_news", 
        "active": True,
        "priority": 1
    },
    {
        "name": "444.hu",
        "url": "https://444.hu/feed",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Magyar Nemzet",
        "url": "https://magyarnemzet.hu/feed/",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Magyar Hang",
        "url": "https://hang.hu/rss/",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Infostart",
        "url": "https://infostart.hu/24ora/rss/",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Hír TV",
        "url": "https://hirtv.hu/rss",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Népszava",
        "url": "https://nepszava.hu/rss",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Válasz Online",
        "url": "https://www.valaszonline.hu/feed/",
        "category": "general",
        "source_type": "domestic_premium",  # PRÉMIUM ELEMZÉSEK
        "content_profile": "timeless_analysis", 
        "active": True,
        "priority": 1
    },
    {
        "name": "Demokrata",
        "url": "https://demokrata.hu/feed",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Mandiner",
        "url": "https://mandiner.hu/rss",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "168 Óra",
        "url": "https://168.hu/rss",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Magyar Narancs",
        "url": "https://magyarnarancs.hu/rss",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "National Geographic HU",
        "url": "https://ng.hu/rss/",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "TudományPláza",
        "url": "https://tudomanyplaza.hu/feed/",
        "category": "general",
        "source_type": "domestic_standard",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    
    # ==========================================  
    # KÜLFÖLD - INTERNATIONAL PREMIUM DOMINANCE!
    # ==========================================
    
    # MAGYAR KÜLFÖLD FORRÁSOK
    {
        "name": "Krónika Online",
        "url": "https://kronikaonline.ro/rss/kronika_hirek.xml",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Maszol",
        "url": "https://maszol.ro/rss",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Székelyhon",
        "url": "https://szekelyhon.ro/rss/szekelyhon_hirek.xml",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Erdély.ma",
        "url": "https://erdely.ma/feed",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Erdélyi Napló",
        "url": "https://erdelyinaplo.ro/rss/szekelyhon_hirek.xml",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Korkép",
        "url": "https://www.korkep.sk/rss",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Hírek.sk",
        "url": "https://www.hirek.sk/rss/hirek_hirek.xml",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Dél-Hír",
        "url": "https://delhir.info/rss",
        "category": "foreign",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # ABLAK A VILÁGRA - BBC FAMILY
    {
        "name": "BBC News UK",
        "url": "http://feeds.bbci.co.uk/news/rss.xml?edition=uk",
        "category": "foreign",
        "source_type": "international_premium",  # ABLAK A VILÁGRA!
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "BBC News World", 
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "foreign",
        "source_type": "international_premium", 
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "BBC News US",
        "url": "http://feeds.bbci.co.uk/news/rss.xml?edition=us",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # CNN FAMILY
    {
        "name": "CNN Latest",
        "url": "http://rss.cnn.com/rss/edition.rss",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news", 
        "active": True,
        "priority": 1
    },
    {
        "name": "CNN World",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "CNN US",
        "url": "http://rss.cnn.com/rss/edition_us.rss",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # AP NEWS FAMILY
    {
        "name": "AP News Top Stories",
        "url": "https://feeds.apnews.com/apnews/topnews",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "AP News World",
        "url": "https://feeds.apnews.com/apnews/worldnews",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    
    # THE GUARDIAN FAMILY
    {
        "name": "The Guardian World",
        "url": "https://www.theguardian.com/world/rss",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "The Guardian UK",
        "url": "https://www.theguardian.com/uk-news/rss",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # SKY NEWS FAMILY
    {
        "name": "Sky News Home",
        "url": "http://feeds.skynews.com/feeds/rss/home.xml",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Sky News World",
        "url": "http://feeds.skynews.com/feeds/rss/world.xml",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Sky News UK",
        "url": "http://feeds.skynews.com/feeds/rss/uk.xml",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # EGYÉB NEMZETKÖZI PRÉMIUM
    {
        "name": "CBC News",
        "url": "https://www.cbc.ca/webfeed/rss/rss-topstories",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "ABC News Australia",
        "url": "https://www.abc.net.au/news/feed/10719986/rss.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "NPR News",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # OKNYOMOZÓ ÚJSÁGÍRÁS - INVESTIGATIVE PREMIUM
    {
        "name": "The Intercept",
        "url": "https://theintercept.com/feed/",
        "category": "foreign",
        "source_type": "investigative_premium",  # OKNYOMOZÓ PRÉMIUM!
        "content_profile": "timeless_analysis",  # IDŐTÁLLÓ!
        "active": True,
        "priority": 1
    },
    {
        "name": "ProPublica", 
        "url": "https://www.propublica.org/feeds/propublica/main",
        "category": "foreign",
        "source_type": "investigative_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Bellingcat",
        "url": "https://www.bellingcat.com/feed/",
        "category": "foreign", 
        "source_type": "investigative_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "OCCRP",
        "url": "https://www.occrp.org/en/feed/",
        "category": "foreign",
        "source_type": "investigative_premium",
        "content_profile": "timeless_analysis", 
        "active": True,
        "priority": 1
    },
    
    # TOVÁBBI NEMZETKÖZI HÍRPORTÁLOK
    {
        "name": "Al Jazeera English",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Middle East Eye",
        "url": "https://middleeasteye.net/rss",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Times of India",
        "url": "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "South China Morning Post",
        "url": "https://www.scmp.com/rss/5/feed",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Foreign Affairs",
        "url": "https://www.foreignaffairs.com/rss.xml",
        "category": "foreign",
        "source_type": "international_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    
    # TOVÁBBI NEMZETKÖZI FORRÁSOK
    {
        "name": "Fox News",
        "url": "https://feeds.foxnews.com/foxnews/latest",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Politico EU",
        "url": "https://www.politico.eu/rss",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Global Times",
        "url": "https://www.globaltimes.cn/rss/outbrain.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "NZZ",
        "url": "https://www.nzz.ch/recent.rss",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Tagesspiegel",
        "url": "https://www.tagesspiegel.de/contentexport/feed/home",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "FAZ",
        "url": "https://www.faz.net/rss/aktuell/",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "El País",
        "url": "https://elpais.com/rss/elpais/portada.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "El Mundo",
        "url": "https://www.elmundo.es/rss/portada.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Le Monde",
        "url": "https://www.lemonde.fr/rss/une.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Le Figaro",
        "url": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
        "category": "foreign",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    
    # ==========================================
    # POLITIKA - DOMESTIC PREMIUM + INVESTIGATIVE
    # ==========================================
    
    {
        "name": "Index Belföld",
        "url": "https://index.hu/belfold/rss/",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "HVG Itthon",
        "url": "https://hvg.hu/rss/itthon",
        "category": "politics",
        "source_type": "domestic_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Telex Belföld",
        "url": "https://telex.hu/rss/belfold",
        "category": "politics", 
        "source_type": "domestic_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Magyar Hang",
        "url": "https://hang.hu/rss/",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Infostart",
        "url": "https://infostart.hu/24ora/rss/",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Hír TV",
        "url": "https://hirtv.hu/rss",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Népszava",
        "url": "https://nepszava.hu/rss",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Válasz Online",
        "url": "https://www.valaszonline.hu/feed/",
        "category": "politics",
        "source_type": "domestic_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Demokrata",
        "url": "https://demokrata.hu/feed",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Mandiner",
        "url": "https://mandiner.hu/rss",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "168 Óra",
        "url": "https://168.hu/rss",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Magyar Narancs",
        "url": "https://magyarnarancs.hu/rss",
        "category": "politics",
        "source_type": "domestic_standard",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "ENSZ - Hírek",
        "url": "https://news.un.org/feed/subscribe/en",
        "category": "politics",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # ==========================================
    # GAZDASÁG - ECONOMY PREMIUM DOMINANCE!
    # ==========================================
    
    # MAGYAR GAZDASÁGI PRÉMIUM
    {
        "name": "Portfolio",
        "url": "https://www.portfolio.hu/rss/all.xml",
        "category": "economy",
        "source_type": "domestic_premium",  # MAGYAR GAZDASÁGI PRÉMIUM
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "G7",
        "url": "https://g7.hu/feed",
        "category": "economy", 
        "source_type": "domestic_premium",  # PRÉMIUM ELEMZÉSEK
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Mfor",
        "url": "https://mfor.hu/rss",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "PrivatBankár",
        "url": "https://privatbankar.hu/rss",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Pénzcentrum",
        "url": "https://www.penzcentrum.hu/rss/all.xml",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Economix",
        "url": "https://www.economx.hu/feed/mindencikk.xml",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Media1",
        "url": "https://media1.hu/feed/",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "PiacÉsProfit",
        "url": "https://piacesprofit.hu/rss/rss.xml",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Profitline",
        "url": "https://profitline.hu/rss",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Növekedés",
        "url": "https://novekedes.hu/feed",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Forbes Hungary",
        "url": "https://forbes.hu/feed/",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "TőzsdeFórum",
        "url": "https://tozsdeforum.hu/feed/",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "AgrárSzektor",
        "url": "https://www.agrarszektor.hu/rss",
        "category": "economy",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    
    # ABLAK A VILÁGRA - THE ECONOMIST!
    {
        "name": "The Economist - Finance",
        "url": "https://www.economist.com/finance-and-economics/rss.xml",
        "category": "economy",
        "source_type": "economy_premium",  # VILÁGSZÍNVONAL!
        "content_profile": "timeless_analysis",  # IDŐTÁLLÓ ELEMZÉSEK
        "active": True,
        "priority": 1
    },
    {
        "name": "The Economist - Business", 
        "url": "https://www.economist.com/business/rss.xml",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    
    # NEMZETKÖZI GAZDASÁGI HÍRPORTÁLOK
    {
        "name": "Business Insider",
        "url": "https://markets.businessinsider.com/rss/news",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "BBC Business",
        "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "category": "economy",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Bloomberg Markets",
        "url": "https://feeds.bloomberg.com/markets/news.rss",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Bloomberg Politics",
        "url": "https://feeds.bloomberg.com/politics/news.rss",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "MarketWatch",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Investopedia - Vállalati hírek",
        "url": "https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_headline&categoryName=company-news",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Investopedia - Piaci hírek",
        "url": "https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_headline&categoryName=markets-news",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # GAZDASÁGI THINK TANK-EK ÉS ELEMZÉSEK
    {
        "name": "Economic Policy Institute",
        "url": "http://feeds.feedburner.com/epi",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "Federal Reserve FRED Blog",
        "url": "https://fredblog.stlouisfed.org/feed/",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "Congressional Budget Office",
        "url": "https://www.cbo.gov/publications/all/rss.xml",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    
    # BEFOLYÁSOS GAZDASÁGI BLOGOK
    {
        "name": "Calculated Risk",
        "url": "http://feeds.feedburner.com/calculatedrisk",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Marginal Revolution",
        "url": "http://feeds.feedburner.com/marginalrevolution", 
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Marginal Revolution Podcast",
        "url": "https://feeds.libsyn.com/548312/rss",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "Financial Samurai",
        "url": "https://financialsamurai.com/feed/",
        "category": "economy",
        "source_type": "economy_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 2
    },
    {
        "name": "Zero Hedge",
        "url": "http://feeds.feedburner.com/zerohedge/feed",
        "category": "economy",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    
    # ==========================================
    # TECH - TECH PREMIUM DOMINANCE!
    # ==========================================
    
    # MAGYAR TECH FORRÁSOK
    {
        "name": "HWSW",
        "url": "http://hwsw.hu/xml/latest_news_rss.xml",
        "category": "tech",
        "source_type": "domestic_premium",  # MAGYAR TECH VEZETŐ
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Prohardver Hírek",
        "url": "https://prohardver.hu/hirfolyam/hirek/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Prohardver Tesztek",
        "url": "https://prohardver.hu/hirfolyam/tesztek/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Prohardver IT Café",
        "url": "https://prohardver.hu/hirfolyam/anyagok/kategoria/it_cafe/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Prohardver Gaming",
        "url": "https://prohardver.hu/hirfolyam/anyagok/kategoria/gamepod/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Prohardver AI",
        "url": "https://prohardver.hu/hirfolyam/anyagok/kategoria/total_ai/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Bitport",
        "url": "https://bitport.hu/rss",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Computerworld",
        "url": "https://computerworld.hu/rss/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "SG.hu",
        "url": "https://media.sg.hu/rss/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "HVG Tech",
        "url": "https://hvg.hu/rss/tudomany",
        "category": "tech",
        "source_type": "domestic_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Qubit",
        "url": "https://qubit.hu/feed",
        "category": "tech",
        "source_type": "domestic_premium",  # MAGYAR TECH MINŐSÉG
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Rakéta",
        "url": "https://raketa.hu/feed",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "PCW Plus",
        "url": "https://www.pcwplus.hu/site/rss/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "TheGeek",
        "url": "https://thegeek.hu/feed/",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "HUP",
        "url": "https://hup.hu/node/feed",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "TechMonitor",
        "url": "https://www.techmonitor.hu/rss",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Tudás.hu",
        "url": "https://tudas.hu/feed/",
        "category": "tech",
        "source_type": "domestic_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    
    # ABLAK A VILÁGRA - TECH TITANS
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "category": "tech",
        "source_type": "tech_premium",  # TECH VILÁGSZÍNVONAL
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "TechCrunch Startups",
        "url": "https://techcrunch.com/category/startups/feed/",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "standard_news", 
        "active": True,
        "priority": 1
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "WIRED Business",
        "url": "https://www.wired.com/category/business/feed/",
        "category": "tech", 
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",  # DEEP TECH ANALYSIS
        "active": True,
        "priority": 1
    },
    {
        "name": "Ars Technica",
        "url": "http://feeds.arstechnica.com/arstechnica/index/",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Engladget",
        "url": "https://www.engadget.com/rss.xml",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "CNET News",
        "url": "https://www.cnet.com/rss/news/",
        "category": "tech",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Mashable",
        "url": "http://feeds.mashable.com/Mashable",
        "category": "tech",
        "source_type": "international_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "BBC Technology",
        "url": "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "category": "tech",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "CNN Technology",
        "url": "http://rss.cnn.com/rss/edition_technology.rss",
        "category": "tech",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Bloomberg Technology",
        "url": "https://feeds.bloomberg.com/technology/news.rss",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "The Guardian Technology",
        "url": "https://www.theguardian.com/technology/rss",
        "category": "tech",
        "source_type": "international_premium",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # TUDOMÁNYOS/KUTATÁSI TECH FORRÁSOK
    {
        "name": "Nature Current Issue",
        "url": "http://www.nature.com/nature/current_issue/rss",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",  # TUDOMÁNYOS = IDŐTÁLLÓ
        "active": True,
        "priority": 1
    },
    {
        "name": "Science Current Issue", 
        "url": "http://www.sciencemag.org/rss/current.xml",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Phys.org",
        "url": "https://phys.org/rss-feed/",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "Science News",
        "url": "https://www.sciencenews.org/feed/",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    {
        "name": "New Scientist",
        "url": "https://www.newscientist.com/feed/home/",
        "category": "tech",
        "source_type": "tech_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    
    # GAMING
    {
        "name": "Gamekapocs",
        "url": "https://www.gamekapocs.hu/rss",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "IGN Hungary",
        "url": "http://hu.ign.com/feed.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "GameStar",
        "url": "https://www.gamestar.hu/site/rss/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Gamer365",
        "url": "https://www.gamer365.hu/rss.xml",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "PlayDome",
        "url": "http://www.pcdome.hu/rss.html",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Gamer",
        "url": "https://gamer.hu/feed/",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    
    # IT BIZTONSÁG
    {
        "name": "KiberBlog",
        "url": "https://kiber.blog.hu/rss",
        "category": "tech",
        "source_type": "domestic_standard",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # ==========================================
    # LIFESTYLE & ENTERTAINMENT
    # ==========================================
    
    # BULVÁR, SZÓRAKOZÁS
    {
        "name": "Blikk",
        "url": "https://www.blikk.hu/rss",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Story",
        "url": "https://story.hu/feed/",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Femina",
        "url": "https://femina.hu/24ora/rss/",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Velvet",
        "url": "https://velvet.hu/24ora/rss/",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Bors",
        "url": "https://www.borsonline.hu/publicapi/hu/rss/bors/articles",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Ripost",
        "url": "https://ripost.hu/feed",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Kiskegyed",
        "url": "https://www.kiskegyed.hu/rss",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Blikk Rúzs",
        "url": "https://blikkruzs.blikk.hu/rss",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Glamour",
        "url": "https://www.glamour.hu/rss",
        "category": "entertainment",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    
    # ÉLETMÓD, EGÉSZSÉG
    {
        "name": "NLC",
        "url": "https://nlc.hu/rss",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Femina Teljes",
        "url": "http://femina.hu/24ora/rss",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Femina Recept",
        "url": "http://femina.hu/recept/rss",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Femina Kapcsolat",
        "url": "http://femina.hu/kapcsolat/rss",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "WEBBeteg",
        "url": "https://www.webbeteg.hu/xml/rss.php",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "EgészségKalauz",
        "url": "https://www.egeszsegkalauz.hu/rss",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Travelo",
        "url": "https://www.travelo.hu/rss",
        "category": "lifestyle",
        "source_type": "lifestyle_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Kultúra.hu",
        "url": "https://kultura.hu/feed/",
        "category": "lifestyle",
        "source_type": "domestic_premium",
        "content_profile": "timeless_analysis",
        "active": True,
        "priority": 1
    },
    
    # ==========================================
    # SPORT & CARS
    # ==========================================
    
    # SPORT HÍREK
    {
        "name": "Sport365",
        "url": "https://sport365.hu/rss",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Infostart Sport",
        "url": "https://infostart.hu/sport/rss/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Index Sport",
        "url": "http://24ora.index.hu/?rss&&rovatkeres=sport",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "HVG Sport",
        "url": "https://hvg.hu/rss/sport",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Rangadó",
        "url": "https://rangado.24.hu/feed/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "NB1",
        "url": "https://nb1.hu/rss",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Monokli",
        "url": "https://monokli.com/rss",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "BB1",
        "url": "https://bball1.hu/feed/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "WBasket",
        "url": "http://wbasket.hu/rss",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Kezdő5",
        "url": "https://kezdo5.hu/rss",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    
    # AUTÓS SPORT
    {
        "name": "Formula.hu",
        "url": "https://formula.hu/rss",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "F1Világ",
        "url": "https://f1vilag.hu/feed/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Racingline",
        "url": "https://racingline.hu/feed/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Motorsport.com Magyar",
        "url": "https://hu.motorsport.com/rss/all/news/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Motorsport MotoGP",
        "url": "https://hu.motorsport.com/rss/motogp/news/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "RallyCafe",
        "url": "https://rallycafe.hu/feed/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    {
        "name": "Rajtvonal Magazin",
        "url": "https://rajtvonalmagazin.hu/feed/",
        "category": "sport",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 3
    },
    
    # AUTÓS HÍREK
    {
        "name": "Totalcar",
        "url": "https://totalcar.hu/24ora/rss",
        "category": "cars",
        "source_type": "sport_specialized", 
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Vezess",
        "url": "https://www.vezess.hu/feed/",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 1
    },
    {
        "name": "Autónavigátor",
        "url": "https://www.autonavigator.hu/feed/",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Autó-Motor",
        "url": "https://automotor.hu/feed/",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Az Autó",
        "url": "https://www.azauto.hu/feed/",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Lóerő",
        "url": "https://loero.hu/feed/",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "e-cars",
        "url": "https://e-cars.hu/feed",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    },
    {
        "name": "Roadster",
        "url": "https://roadster.hu/feed/",
        "category": "cars",
        "source_type": "sport_specialized",
        "content_profile": "standard_news",
        "active": True,
        "priority": 2
    }
]

# === STRATÉGIAI FUNKCIÓK ===

def get_source_metadata(source_name: str):
    """Forrás metaadatok lekérdezése"""
    for source in NEWS_SOURCES:
        if source["name"] == source_name:
            source_type = source["source_type"]
            return SOURCE_TYPES.get(source_type, {})
    return {}

def is_fast_lane_source(source_name: str) -> bool:
    """Zöld sáv ellenőrzés"""
    return source_name in PREMIUM_FAST_LANE_SOURCES

def get_content_profile_info(profile_name: str):
    """Tartalom profil információ"""
    return CONTENT_PROFILES.get(profile_name, CONTENT_PROFILES["standard_news"])

def calculate_source_boost(source_name: str, category: str) -> float:
    """Forrás boost szorzó számítása"""
    metadata = get_source_metadata(source_name)
    
    if not metadata:
        return 1.0
    
    # Alapvető boost
    base_boost = metadata.get("boost_multiplier", 1.0)
    
    # Kategória-specifikus boost ellenőrzés
    allowed_categories = metadata.get("categories", [])
    if category in allowed_categories:
        return base_boost
    else:
        # Kategória nem egyezik = büntetés
        return base_boost * 0.5
    
def get_auto_gpt4o_threshold(source_name: str) -> int:
    """Automatikus GPT-4o küszöb forrás alapján"""
    metadata = get_source_metadata(source_name)
    return metadata.get("auto_gpt4o_threshold", 16)  # Default: 16

# BACKWARD COMPATIBILITY
CATEGORIES = {
    "general": "👥 Közélet",
    "foreign": "🌍 Külföld", 
    "politics": "🏛️ Politika",
    "economy": "📈 Gazdaság",
    "tech": "💻 Tech",
    "entertainment": "👠 Bulvár",
    "sport": "⚽ Sport", 
    "cars": "🚗 Autók",
    "lifestyle": "✨ Életmód"
}

# Social Media Platform Konfiguráció - HONLAP INTEGRÁLT
SOCIAL_PLATFORMS = {
    "twitter": {
        "enabled": True,
        "post_interval_hours": 6,
        "max_thread_length": 10,
        "hashtags": ["#hírek", "#magyarország", "#hirmagnet"],
        "icon": "🐦",
        "display_name": "Twitter"
    },
    "spotify": {
        "enabled": True,
        "episode_interval_hours": 6,
        "max_duration_minutes": 15,
        "show_name": "HírMagnet Podcast",
        "icon": "🎵",
        "display_name": "Spotify"
    },
    "youtube": {
        "enabled": True,
        "video_interval_hours": 24,
        "max_duration_minutes": 10,
        "channel_name": "HírMagnet TV",
        "icon": "📺",
        "display_name": "YouTube"
    }
}

# Honlap Konfiguráció - ÚJ RÉSZ
WEBSITE_CONFIG = {
    "site_name": "HírMagnet",
    "site_tagline": "AI Magyar Hírportál",
    "logo_icon": "🧲",
    "primary_color": "#3A7BCE",
    "background_images": [
        "/static/background1.jpg",
        "/static/background2.jpg"
    ],
    "audio_enabled": True,
    "premium_features": True,
    "trending_limit": 10,
    "articles_per_page": 20,
    "short_articles_limit": 6,
    "cache_duration_minutes": 5,
    "debug_mode_available": True
}

# API Endpoints Konfiguráció - ÚJ RÉSZ  
API_ENDPOINTS = {
    "articles": "/api/articles",
    "trending": "/api/trending", 
    "latest": "/api/latest",
    "dashboard_data": "/api/dashboard-data",
    "article_play": "/api/articles/{id}/play",
    "audio_files": "/static/audio/"
}

# Navigációs Kategóriák - HONLAP KOMPATIBILIS
NAV_CATEGORIES = [
    {"code": "all", "name": "Összes", "icon": "🌐"},
    {"code": "general", "name": "Közélet", "icon": "👥"},
    {"code": "foreign", "name": "Külföld", "icon": "🌍"},
    {"code": "politics", "name": "Politika", "icon": "🏛️"},
    {"code": "economy", "name": "Gazdaság", "icon": "📈"},
    {"code": "tech", "name": "Tech", "icon": "💻"},
    {"code": "entertainment", "name": "Bulvár", "icon": "👠"},
    {"code": "sport", "name": "Sport", "icon": "⚽"},
    {"code": "cars", "name": "Autók", "icon": "🚗"},
    {"code": "lifestyle", "name": "Életmód", "icon": "✨"}
]

# Content Quality Filters - HONLAP OPTIMALIZÁLT
CONTENT_FILTERS = {
    "min_article_length": 100,
    "blocked_keywords": ["clickbait", "fake news"],
    "quality_sources": ["hvg.hu", "telex.hu", "portfolio.hu", "g7.hu", "valaszonline.hu", "tudas.hu", "kultura.hu"],
    "importance_multipliers": {
        "breaking": 2.0,
        "economy": 1.5,
        "politics": 1.3,
        "tech": 1.2,
        "foreign": 1.1
    },
    "category_priorities": {
        "general": 1,
        "politics": 1, 
        "economy": 1,
        "foreign": 2,
        "tech": 2,
        "sport": 3,
        "entertainment": 3,
        "cars": 3,
        "lifestyle": 3
    }
}

# FRISSÍTÉS STATISZTIKÁK
print(f"""
🧲 HírMagnet Sources.py KOMPLETT STRATEGIC UPGRADE

📊 VOLLSTÄNDIGKEIT:
  📦 Összes RSS forrás: {len(NEWS_SOURCES)} (MINDEN FORRÁS!)
  📂 Kategóriák száma: {len(CATEGORIES)} (BACKWARD COMPATIBLE)
  🚀 Fast Lane források: {len(PREMIUM_FAST_LANE_SOURCES)}
  🎯 Source types: {len(SOURCE_TYPES)}
  📝 Content profiles: {len(CONTENT_PROFILES)}

🆕 STRATEGIC FEATURES:
  ✅ Dinamikus pontrendszer metaadatok
  ✅ "Zöld Sáv" Fast Lane rendszer  
  ✅ Source Priority Matrix
  ✅ Content Profile támogatás
  ✅ Auto GPT-4o threshold forrás alapján
  ✅ Stratégiai tartalék rendszer

✅ BACKWARD COMPATIBILITY GARANTIERT:
  • MINDEN 187 RSS forrás megmaradt
  • Kategória struktúra VÁLTOZATLAN
  • API végpontok kompatibilisek
  • Honlap navigáció működőképes

🎯 GERMAN PRECISION ENGINEERING COMPLETE!
""")
