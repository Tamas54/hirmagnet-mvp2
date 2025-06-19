import os
import sys
from datetime import datetime, timedelta
import glob

# Projekt gyökér könyvtár hozzáadása
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db_session
from database.models import Article, ProcessingLog, SiteStats
from config.settings import AUDIO_DIR

def cleanup_old_articles(days_old=30):
    """Régi cikkek törlése (csak a nagyon régiek)"""
    db = get_db_session()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Régi cikkek lekérdezése
        old_articles = db.query(Article).filter(
            Article.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        
        for article in old_articles:
            try:
                # Kapcsolódó hangfájl törlése
                if article.audio_filename:
                    audio_path = os.path.join(AUDIO_DIR, article.audio_filename)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                
                # Cikk törlése adatbázisból
                db.delete(article)
                deleted_count += 1
                
            except Exception as e:
                print(f"⚠️ Cikk törlési hiba: {str(e)}")
                continue
        
        db.commit()
        
        print(f"🗑️ {deleted_count} régi cikk törölve ({days_old} napnál régebbiek)")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Cikk cleanup hiba: {str(e)}")
        db.rollback()
        return 0
    finally:
        db.close()

def cleanup_old_logs(days_old=7):
    """Régi log bejegyzések törlése"""
    db = get_db_session()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        deleted_count = db.query(ProcessingLog).filter(
            ProcessingLog.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        
        print(f"🗑️ {deleted_count} régi log bejegyzés törölve")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Log cleanup hiba: {str(e)}")
        db.rollback()
        return 0
    finally:
        db.close()

def cleanup_orphaned_audio_files():
    """Árva hangfájlok törlése (adatbázisban nem szereplő fájlok)"""
    db = get_db_session()
    
    try:
        # Adatbázisban szereplő hangfájlok
        db_audio_files = set()
        articles_with_audio = db.query(Article).filter(
            Article.audio_filename.isnot(None)
        ).all()
        
        for article in articles_with_audio:
            if article.audio_filename:
                db_audio_files.add(article.audio_filename)
        
        # Fizikai hangfájlok a mappában
        if not os.path.exists(AUDIO_DIR):
            print("📁 Audio mappa nem létezik")
            return 0
        
        physical_files = set()
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith('.mp3'):
                physical_files.add(filename)
        
        # Árva fájlok (fizikailag léteznek, de adatbázisban nincsenek)
        orphaned_files = physical_files - db_audio_files
        
        deleted_count = 0
        for filename in orphaned_files:
            try:
                file_path = os.path.join(AUDIO_DIR, filename)
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Árva fájl törlési hiba {filename}: {str(e)}")
                continue
        
        print(f"🗑️ {deleted_count} árva hangfájl törölve")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Árva fájl cleanup hiba: {str(e)}")
        return 0
    finally:
        db.close()

def cleanup_log_files(days_old=14):
    """Régi log fájlok törlése"""
    try:
        log_dir = "data/logs"
        if not os.path.exists(log_dir):
            return 0
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        for log_file in glob.glob(os.path.join(log_dir, "*.log")):
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                
                if file_mtime < cutoff_time:
                    os.remove(log_file)
                    deleted_count += 1
                    
            except Exception as e:
                print(f"⚠️ Log fájl törlési hiba {log_file}: {str(e)}")
                continue
        
        print(f"🗑️ {deleted_count} régi log fájl törölve")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Log fájl cleanup hiba: {str(e)}")
        return 0

def optimize_database():
    """Adatbázis optimalizálás (SQLite VACUUM)"""
    try:
        from database.db import engine
        
        # SQLite VACUUM parancs
        with engine.connect() as conn:
            conn.execute("VACUUM")
        
        print("🔧 Adatbázis optimalizálva (VACUUM)")
        return True
        
    except Exception as e:
        print(f"❌ Adatbázis optimalizálási hiba: {str(e)}")
        return False

def update_site_stats():
    """Oldal statisztikák frissítése"""
    db = get_db_session()
    
    try:
        from sqlalchemy import func
        
        # Mai statisztikák
        today = datetime.now().date()
        
        # Cikkek száma
        total_articles = db.query(Article).count()
        
        # Mai nézettség (egyszerű becslés - ezt valós analytics-szel kell helyettesíteni)
        daily_views = db.query(func.sum(Article.view_count)).scalar() or 0
        daily_audio_plays = db.query(func.sum(Article.audio_play_count)).scalar() or 0
        
        # Top kategória
        top_category = db.query(
            Article.category,
            func.count(Article.id).label('count')
        ).group_by(Article.category).order_by(
            func.count(Article.id).desc()
        ).first()
        
        top_category_name = top_category[0] if top_category else "general"
        
        # Statisztika mentés
        stat = SiteStats(
            total_articles=total_articles,
            daily_views=daily_views,
            daily_audio_plays=daily_audio_plays,
            top_category=top_category_name,
            unique_visitors=0  # Ezt Google Analytics-ből kellene venni
        )
        
        db.add(stat)
        db.commit()
        
        print(f"📊 Statisztikák frissítve: {total_articles} cikk, {daily_views} nézettség")
        return True
        
    except Exception as e:
        print(f"❌ Statisztika frissítési hiba: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def cleanup_old_data():
    """Teljes cleanup folyamat"""
    print(f"\n🧹 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Cleanup indítása")
    
    total_operations = 0
    
    # 1. Régi cikkek törlése (30 napnál régebbiek)
    total_operations += cleanup_old_articles(days_old=30)
    
    # 2. Régi logok törlése (7 napnál régebbiek)
    total_operations += cleanup_old_logs(days_old=7)
    
    # 3. Árva hangfájlok törlése
    total_operations += cleanup_orphaned_audio_files()
    
    # 4. Régi log fájlok törlése
    total_operations += cleanup_log_files(days_old=14)
    
    # 5. Adatbázis optimalizálás
    if optimize_database():
        total_operations += 1
    
    # 6. Statisztikák frissítése
    if update_site_stats():
        total_operations += 1
    
    print(f"✅ Cleanup befejezve: {total_operations} művelet végrehajtva")
    return total_operations

def main():
    """Cleanup kézi futtatáshoz"""
    cleanup_old_data()

if __name__ == "__main__":
    main()