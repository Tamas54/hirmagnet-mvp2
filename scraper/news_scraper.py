# news_scraper.py - OPERATION STAHLFILTER & STRATEGISCHE PRIORITÄT UPGRADE
# German Engineering Precision by Oberleutnant von Program

import feedparser
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.db import get_db_session
from database.models import Article, ProcessingLog
from config.sources import NEWS_SOURCES
from config.settings import MAX_ARTICLES_PER_SOURCE, REQUEST_TIMEOUT
import time
import hashlib
from dateutil import parser as date_parser

# === TAKTIKAI DEKONTAMINÁCIÓS EGYSÉG IMPORTÁLÁSA ===
import re
from bs4 import BeautifulSoup
# ====================================================


# === JAVÍTÁS: STAHLFILTER KONFIGURÁCIÓ (SZÓ-ALAPÚ) ===
MINIMUM_WORD_COUNT = 100  # Az Acélszűrő minimális szólimtje
# =======================================================

class NewsScraperError(Exception):
    pass

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        })
        
    def scrape_all_sources(self):
        """Összes aktív forrás lescrapelése STRATÉGIAI PRIORITÁS szerint."""
        total_new_articles = 0
        db = get_db_session()
        
        start_time = time.time()
        
        try:
            # A források sorba rendezése a `priority` mező alapján
            sorted_sources = sorted([s for s in NEWS_SOURCES if s.get('active', True)], key=lambda x: x.get('priority', 99))
            print(f"🎖️ Stratégiai sorrend felállítva. {len(sorted_sources)} aktív forrás a célkeresztben.")

            for source in sorted_sources:
                print(f"\n🔍 Támadás alatt: {source['name']} (Prioritás: {source.get('priority', 'N/A')})")
                try:
                    new_count = self._scrape_single_source(source, db)
                    total_new_articles += new_count
                    if new_count > 0:
                        print(f"✅ Sikeres behatolás: {source['name']} - {new_count} új cikk biztosítva.")
                    else:
                        print(f"ⓘ {source['name']}: Nincs új harcászati értékű információ.")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    error_message = f"Hiba a(z) '{source['name']}' frontszakaszán: {str(e)}"
                    print(f"❌ {error_message}")
                    self._log_error(db, "scraping", source['name'], error_message)
                    continue
            
            processing_time = time.time() - start_time
            
            log = ProcessingLog(
                action="scraping_v2_strategic",
                articles_processed=total_new_articles,
                success=True,
                processing_time=processing_time
            )
            db.add(log)
            db.commit()
            
            print(f"\n🎉 SCRAPING HADMŰVELET BEFEJEZVE! Összesen {total_new_articles} új cikk biztosítva {processing_time:.1f} másodperc alatt.")
            return total_new_articles
            
        except Exception as e:
            self._log_error(db, "scraping", "general", str(e))
            raise NewsScraperError(f"Általános scraping hiba: {str(e)}")
        finally:
            db.close()

    def _clean_html_content(self, html_content: str) -> str:
        """Taktikai Dekontaminációs eljárás a nyers HTML tartalomhoz."""
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            return re.sub(r'\s+', ' ', text).strip()
        except Exception:
            text = re.sub(r'<[^>]+>', '', html_content)
            return re.sub(r'\s+', ' ', text).strip()

    def _scrape_single_source(self, source, db: Session):
        """Egy forrás lescrapelése"""
        try:
            response = self.session.get(source['url'], timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            if not feed.entries: return 0
            
            new_articles = 0
            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                try:
                    if self._save_article(entry, source, db):
                        new_articles += 1
                except Exception as e:
                    print(f"  ⚠️ Cikk mentési hiba ({entry.get('link', 'N/A')}): {str(e)}")
                    continue
            return new_articles
        except Exception as e:
            raise Exception(f"RSS letöltési hiba")
    
    def _save_article(self, entry, source_config, db: Session):
        """Cikk mentése az adatbázisba a megerősített STAHLFILTER doktrínával."""
        try:
            article_url = entry.get('link', '')
            if not article_url: return False
                
            existing = db.query(Article).filter(Article.url == article_url).first()
            if existing: return False
            
            title = entry.get('title', '').strip()
            if not title: return False
                
            published_at = None
            if 'published' in entry:
                try:
                    published_at = date_parser.parse(entry.published)
                except:
                    pass
            
            raw_content = ""
            if 'summary' in entry:
                raw_content = entry.summary
            elif 'description' in entry:
                raw_content = entry.description

            clean_content = self._clean_html_content(raw_content)

            # === JAVÍTÁS: STAHLFILTER DOKTRÍNA (SZÓ-ALAPÚ) ===
            # A karakterek helyett a szavak számát ellenőrizzük
            word_count = len(clean_content.split())
            if word_count < MINIMUM_WORD_COUNT:
                #print(f"  🛡️ STAHLFILTER: Cikk elutasítva - túl rövid ({word_count} szó). Cím: {title[:50]}...")
                return False
            # ===============================================
            
            article = Article(
                title=title,
                original_title=title,
                original_content=clean_content,
                url=article_url,
                source=source_config['name'],
                category=source_config.get('category', 'general'),
                published_at=published_at,
                is_processed=False
            )
            
            db.add(article)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Adatbázis mentési hiba: {str(e)}")
    
    def _log_error(self, db: Session, action: str, source: str, error: str):
        """Hiba naplózása"""
        try:
            log = ProcessingLog(action=action, source=source, success=False, error_message=error[:1000])
            db.add(log)
            db.commit()
        except:
            pass

def main():
    """Fő scraping függvény (cron job-hoz)"""
    scraper = NewsScraper()
    try:
        new_articles = scraper.scrape_all_sources()
        print(f"✅ Scraping kész: {new_articles} új cikk")
        return new_articles
    except Exception as e:
        print(f"❌ KRITIKUS SCRAPING HIBA: {str(e)}")
        return 0

if __name__ == "__main__":
    main()
