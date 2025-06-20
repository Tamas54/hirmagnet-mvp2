# test_master.py - FIXED VERSION
# A VÉGSŐ, KOMPLETT, MŰKÖDŐKÉPES TESZT-PROTOKOLL

import asyncio
import argparse
import random
import re
from typing import List, Dict, Any
from datetime import datetime

# A rendszer minden szükséges komponensének importálása
from database.db import get_db_session
from database.models import Article
from scraper.news_scraper import NewsScraper
from ai.editorial_ai import StrategicEditorialAI
from ai.v5_orchestrator import ChimeraDualChannelOrchestrator
from config.sources import NEWS_SOURCES

# === TESZT KONFIGURÁCIÓ ===
QUICK_MODE_SOURCES = [
    # MAGYAR PRÉMIUM
    'Telex', 'HVG', 'Index', '24.hu', 'Válasz Online', 'G7', 'Portfolio',
    
    # MAGYAR STANDARD  
    '444.hu', 'Magyar Nemzet', 'Maszol',
    
    # BBC CSALÁD
    'BBC News UK', 'BBC News World', 'BBC Business', 'BBC Technology',
    
    # GUARDIAN CSALÁD  
    'The Guardian World', 'The Guardian UK', 'The Guardian Technology',
    
    # CNN CSALÁD
    'CNN Latest', 'CNN World', 'CNN Technology',
    
    # GAZDASÁGI PRÉMIUM
    'The Economist - Finance', 'The Economist - Business', 'Bloomberg Markets',
    
    # TECH PRÉMIUM
    'TechCrunch', 'TechCrunch Startups', 'The Verge', 'WIRED Business',
    
    # OKNYOMOZÓ PRÉMIUM
    'Bellingcat', 'The Intercept', 'ProPublica', 'OCCRP',
    
    # TOVÁBBI NEMZETKÖZI
    'Fox News', 'Politico EU', 'AP News Top Stories', 'Sky News Home',
    
    # NÉMET FORRÁSOK
    'FAZ', 'Tagesspiegel', 'NZZ'
]
ARTICLE_FETCH_LIMIT_QUICK = 5
ARTICLE_FETCH_LIMIT_COMPLETE = 10
# =================================

def print_pipeline_report(editorial_results: Dict, final_dispositions: List[Dict]):
    """A csővezeték elemzésének riportja (cikkírás nélkül)."""
    scraped_count = editorial_results.get("scraped_count", 0)
    kept_count = len(editorial_results.get("kept", []))
    dup_count = len(editorial_results.get("duplicates", []))

    print("\n" + "="*130)
    print(f"{'📊 CSŐVEZETÉK-ELEMZÉSI JELENTÉS 📊':^130}")
    print("="*130)

    print("\n--- 1-2. FÁZIS: HÍRSZERZÉS ÉS SZERKESZTŐI SZŰRÉS ---")
    print(f"Begyűjtött cikkek: {scraped_count} db | AI által egyedinek ítélt: {kept_count} db | Kiszűrt duplikátum: {dup_count} db")

    if not final_dispositions:
        print("\nNincs tovább feldolgozott cikk a riportoláshoz.")
        print("="*130)
        return

    print("\n--- 3-4. FÁZIS: ORCHESTRATOR - CSATORNAKIOSZTÁS ÉS PARANCSKIADÁS (TELJES LISTA) ---")
    header = f"| {'#':<3} | {'Forrás':<20} | {'Cím (Részlet)':<45} | {'AI Kategória':<12} | {'AI Pont':<7} | {'Csatorna':<10} | {'Újságíró':<22} |"
    print(header)
    print(f"|{'-'*5}|{'-'*22}|{'-'*47}|{'-'*14}|{'-'*9}|{'-'*12}|{'-'*24}|")

    for i, disp in enumerate(final_dispositions):
        title_short = (disp.get('title', 'N/A')[:43] + '..') if len(disp.get('title', 'N/A')) > 45 else disp.get('title', 'N/A')
        row = (f"| {i+1:<3} | {disp.get('source', 'N/A'):<20} | {title_short:<45} | "
               f"{disp.get('category', 'N/A'):<12} | {disp.get('importance', 'N/A'):<7} | "
               f"{disp.get('channel', 'N/A'):<10} | {disp.get('journalist', 'N/A'):<22} |")
        print(row)
    
    print("="*130)

def print_generation_report(processed_articles: List[Article]):
    """A legenerált cikkek riportja."""
    print("\n" + "="*125)
    print(f"{'✒️ ÉLESLÖVÉSZET - ELKÉSZÜLT CIKKEK JELENTÉSE ✒️':^125}")
    print("="*125)
    
    if not processed_articles:
        print("A feldolgozás során nem generálódott új cikk.")
        print("="*125)
        return
        
    for i, art in enumerate(processed_articles):
        print(f"\n\n--- CIKK #{i+1} ---")
        ai_title = art.ai_title or "GENERÁLT CÍM HIÁNYZIK"
        signature = f"{art.journalist_name}, HírMagnet" if art.journalist_name else "HírMagnet Szerkesztőség"
        summary = art.ai_summary or "A TARTALOM GENERÁLÁSA SIKERTELEN VAGY HIÁNYOS."
        
        print(f"Forrás: {art.source}")
        print(f"Eredeti Cím: {art.original_title}")
        print("-" * 25)
        print(f"GENERÁLT CÍM: {ai_title}")
        print(f"SZIGNÓ: {signature}")
        print(f"AI Kategória: {art.category} | AI Pontszám: {int(art.importance_score or 0)}/20")
        print("-" * 25)
        print("\nGENERÁLT TARTALOM:\n")
        print(summary)
        print("\n" + "="*50 + f" CIKK #{i+1} VÉGE " + "="*51)

    print("\n\n✅ Inspekció befejezve.")

def _get_dispositions_from_channels(orchestrator, channels):
    """Segédfüggvény a riportoláshoz szükséges adatok kinyerésére."""
    final_dispositions = []
    
    # Blitz channel feldolgozása
    blitz_articles = channels.get('blitz', [])
    for article in blitz_articles:
        # Újságíró kiválasztás (ha van journalist manager)
        journalist_assignment = None
        journalist_name = "N/A"
        
        try:
            if hasattr(orchestrator, 'processor') and orchestrator.processor.journalist_manager:
                journalist_assignment = orchestrator.processor.journalist_manager.select_journalist_for_article(
                    getattr(article, 'category', 'general'),
                    getattr(article, 'importance_score', 8),
                    getattr(article, 'original_content', '') or ''
                )
                if journalist_assignment:
                    journalist_name = journalist_assignment.get('journalist_name', 'N/A')
        except:
            pass
        
        final_dispositions.append({
            'title': getattr(article, 'original_title', 'N/A'),
            'source': getattr(article, 'source', 'N/A'),
            'category': getattr(article, 'category', 'N/A'),
            'importance': getattr(article, 'importance_score', 'N/A'),
            'channel': 'Blitz',
            'journalist': journalist_name
        })
    
    # Strategic channel feldolgozása
    strategic_articles = channels.get('strategic', [])
    for article in strategic_articles:
        # Újságíró kiválasztás (ha van journalist manager)
        journalist_assignment = None
        journalist_name = "N/A"
        
        try:
            if hasattr(orchestrator, 'processor') and orchestrator.processor.journalist_manager:
                journalist_assignment = orchestrator.processor.journalist_manager.select_journalist_for_article(
                    getattr(article, 'category', 'general'),
                    getattr(article, 'importance_score', 8),
                    getattr(article, 'original_content', '') or ''
                )
                if journalist_assignment:
                    journalist_name = journalist_assignment.get('journalist_name', 'N/A')
        except:
            pass
        
        final_dispositions.append({
            'title': getattr(article, 'original_title', 'N/A'),
            'source': getattr(article, 'source', 'N/A'),
            'category': getattr(article, 'category', 'N/A'),
            'importance': getattr(article, 'importance_score', 'N/A'),
            'channel': 'Strategic',
            'journalist': journalist_name
        })
    
    return final_dispositions

async def run_master_test(mode: str, force_scrape: bool, generate_content: bool):
    """Az univerzális teszt-szkript fő logikája."""
    print(f"🎯 Operation 'Meisterstück' indul... Módusz: '{mode.upper()}' | Force Scrape: {force_scrape} | Generate Content: {generate_content}")
    
    # DEBUG: API kulcsok ellenőrzése
    print("🔧 API kulcsok ellenőrzése...")
    import os
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"🔧 OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ MISSING'}")
    print(f"🔧 GEMINI_API_KEY: {'✅ SET' if gemini_key else '❌ MISSING'}")
    
    db = get_db_session()
    
    # 1. LÉPÉS: DINAMIKUS HÍRGYŰJTÉS
    if mode == 'quick':
        target_sources_configs = [s for s in NEWS_SOURCES if s['name'] in QUICK_MODE_SOURCES and s.get('active', True)]
        fetch_limit = ARTICLE_FETCH_LIMIT_QUICK
    else:
        target_sources_configs = [s for s in NEWS_SOURCES if s.get('active', True)]
        fetch_limit = ARTICLE_FETCH_LIMIT_COMPLETE
        
    source_names = [s['name'] for s in target_sources_configs]
    print(f"🔍 Hírszerzés indul... {len(source_names)} forrás a célkeresztben.")
    
    # === A HIÁNYZÓ LOGIKA BEILLESZTVE ===
    scraper = NewsScraper()
    scraped_articles: List[Article] = []
    
    NewsScraper._scrape_single_source_for_entries = _scrape_single_source_for_entries
    NewsScraper._create_article_object_from_entry = _create_article_object_from_entry
    NewsScraper._clean_html_content = lambda self, text: re.sub(r'<[^>]+>', '', text or "")

    urls_seen = set() if force_scrape else {row.url for row in db.query(Article.url)}
    all_entries = []

    for source_config in target_sources_configs:
        feed = scraper._scrape_single_source_for_entries(source_config)
        for entry in feed.entries[:fetch_limit]:
            all_entries.append({'entry': entry, 'source_config': source_config})

    all_entries.sort(key=lambda x: x['entry'].get('published_parsed', datetime.min.timetuple()), reverse=True)

    for item in all_entries:
        entry = item['entry']
        article_url = entry.get('link')
        if not article_url or article_url in urls_seen:
            continue
        urls_seen.add(article_url)
        article_obj = scraper._create_article_object_from_entry(entry, item['source_config'])
        if len(article_obj.original_content or "") > 150:
             scraped_articles.append(article_obj)
    # =================================================

    if not scraped_articles:
        print("\n❌ NEM TALÁLHATÓ FELDOLGOZHATÓ CIKK A MEGADOTT KRITÉRIUMOKKAL. A teszt leáll.")
        db.close()
        return

    print(f"✅ Hírszerzés kész: {len(scraped_articles)} cikk begyűjtve.")
    
    # 2. LÉPÉS: ELŐZETES SZŰRÉS (csak ha nincs generálás)
    if not scraped_articles:
        print("✅ Nincs feldolgozható cikk.")
        db.close()
        return
        
    # 3. LÉPÉS: DÖNTÉS A FOLYTATÁSRÓL
    orchestrator = ChimeraDualChannelOrchestrator()
    if not generate_content:
        print("🤖 Cikk-generálás KIHAGYVA. Csővezeték-elemzés riportolása...")
        
        # CSAK pipeline elemzéshez hívjuk meg az Editorial AI-t
        editorial_ai = StrategicEditorialAI()
        editorial_results = editorial_ai.process_articles_editorial(scraped_articles)
        articles_to_process = editorial_results.get("kept", [])
        
        if not articles_to_process:
            print("✅ Az Editorial AI minden cikket kiszűrt.")
            db.close()
            return
            
        channels = orchestrator.categorize_articles_by_channel(articles_to_process)
        final_dispositions = _get_dispositions_from_channels(orchestrator, channels)
        editorial_results["scraped_count"] = len(scraped_articles)
        print_pipeline_report(editorial_results, final_dispositions)
        print("✅ Csővezeték teszt befejezve.")
    else:
        print("✍️ Cikk-generálás INDUL...")
        
        # NINCS Editorial AI hívás itt - az orchestrator végzi!
        # UPSERT Logika - közvetlenül a scraped articles-ekkel
        articles_for_orchestrator = []
        for mem_article in scraped_articles:
            db_article = db.query(Article).filter(Article.url == mem_article.url).first()
            if db_article:
                # Frissítjük a létező cikket
                db_article.original_title = mem_article.original_title
                db_article.original_content = mem_article.original_content
                db_article.is_processed = False
                articles_for_orchestrator.append(db_article)
            else:
                db.add(mem_article)
                articles_for_orchestrator.append(mem_article)
        db.commit()
        
        # Az orchestrator elvégzi az Editorial AI feldolgozást + generálást
        article_ids_to_track = [art.id for art in articles_for_orchestrator]
        print(f"🔧 Database írás - {len(articles_for_orchestrator)} cikk az orchestrator-nak átadva...")
        await orchestrator.run_full_process(articles_for_orchestrator)
        
        print("✅ Cikk-generálási fázis befejezve. Eredmények lekérdezése...")
        processed_articles = db.query(Article).filter(Article.id.in_(article_ids_to_track)).all()
        processed_count = len([art for art in processed_articles if art.ai_title or art.ai_summary])
        print(f"🔧 Új cikkek száma: {processed_count}")
        print_generation_report(processed_articles)
    
    db.close()

# Segédfüggvények, hogy a szkript önállóan futtatható legyen
def _scrape_single_source_for_entries(self, source):
    import feedparser
    try:
        response = self.session.get(source['url'], timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except Exception as e:
        return type('MockFeed', (), {'entries': []})()

def _create_article_object_from_entry(self, entry, source_config):
    from dateutil import parser as date_parser
    title = entry.get('title', '').strip()
    content = entry.summary if 'summary' in entry else entry.description if 'description' in entry else ""
    clean_content = self._clean_html_content(content)
    published_at = None
    if 'published_parsed' in entry and entry.published_parsed:
        published_at = datetime(*entry.published_parsed[:6])
    elif 'published' in entry:
        try: published_at = date_parser.parse(entry.published) 
        except: pass
    return Article(
        title=title, original_title=title, original_content=clean_content,
        url=entry.get('link'), source=source_config['name'], 
        category=source_config.get('category', 'general'), published_at=published_at
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HírMagnet Univerzális Teszt Protokoll v2.1 - FIXED')
    parser.add_argument('--mode', type=str, choices=['quick', 'complete'], default='quick', help="A teszt módusza.")
    parser.add_argument('--force-scrape', action='store_true', help="Figyelmen kívül hagyja a meglévő cikkeket.")
    parser.add_argument('--generate-content', action='store_true', help="Lefuttatja a tényleges cikk-generálást is.")
    args = parser.parse_args()
    
    asyncio.run(run_master_test(args.mode, args.force_scrape, args.generate_content))