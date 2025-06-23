# automation/advanced_scheduler.py
import schedule
import time
import sys
import os
import asyncio
from datetime import datetime

# Projekt gyökér könyvtár hozzáadása
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.news_scraper import NewsScraper
from ai.processor import AIProcessor
from ai.tts import TTSGenerator
from automation.cleanup import cleanup_old_data

# Social Media Publishers
from social.spotify_publisher import create_spotify_podcast
from social.youtube_publisher import create_youtube_newscast
from social.twitter_publisher import create_twitter_thread

class AdvancedAutomationScheduler:
    def __init__(self):
        self.scraper = NewsScraper()
        self.ai_processor = AIProcessor()
        self.tts_generator = TTSGenerator()
        self.is_running = False
        
        # Social media flags
        self.social_enabled = {
            'spotify': os.getenv('SPOTIFY_ENABLED', 'true').lower() == 'true',
            'youtube': os.getenv('YOUTUBE_ENABLED', 'true').lower() == 'true',
            'twitter': os.getenv('TWITTER_ENABLED', 'true').lower() == 'true'
        }
        
    def run_news_scraping(self):
        """Enhanced hírgyűjtés futtatása"""
        print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 🔍 SCRAPING OPERATION")
        try:
            new_articles = self.scraper.scrape_all_sources()
            
            if new_articles > 0:
                print(f"✅ Hírgyűjtés: {new_articles} új cikk")
                
                # Breaking news check
                if new_articles > 20:  # Ha túl sok új hír, lehet breaking news
                    print("🚨 BREAKING NEWS DETECTED - Gyorsított feldolgozás")
                    asyncio.run(self._emergency_processing())
            else:
                print("ℹ️ Nincs új hír")
                
        except Exception as e:
            print(f"❌ Hírgyűjtési hiba: {str(e)}")
    
    def run_ai_processing(self):
        """Enhanced AI feldolgozás"""
        print(f"\n🤖 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - AI PROCESSING")
        try:
            processed = self.ai_processor.process_unprocessed_articles()
            if processed > 0:
                print(f"✅ AI feldolgozás: {processed} cikk")
            else:
                print("ℹ️ Nincs feldolgozatlan cikk")
        except Exception as e:
            print(f"❌ AI feldolgozási hiba: {str(e)}")
    
    def run_tts_generation(self):
        """Enhanced TTS generálás"""
        print(f"\n🎵 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - TTS GENERATION")
        try:
            generated = self.tts_generator.generate_audio_for_unprocessed()
            if generated > 0:
                print(f"✅ TTS generálás: {generated} hangfájl")
            else:
                print("ℹ️ Nincs új TTS feladat")
        except Exception as e:
            print(f"❌ TTS generálási hiba: {str(e)}")
    
    def run_social_media_publishing(self):
        """Social media publikálás koordinálása"""
        print(f"\n📱 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SOCIAL MEDIA PUBLISHING")
        
        results = {}
        
        # Twitter Thread (6 óránként)
        if self.social_enabled['twitter']:
            try:
                print("🐦 Twitter thread készítése...")
                success = asyncio.run(create_twitter_thread())
                results['twitter'] = success
                if success:
                    print("✅ Twitter thread publikálva")
                else:
                    print("⚠️ Twitter thread sikertelen")
            except Exception as e:
                print(f"❌ Twitter hiba: {str(e)}")
                results['twitter'] = False
        
        # Spotify Podcast (6 óránként)
        if self.social_enabled['spotify']:
            try:
                print("🎵 Spotify podcast készítése...")
                success = asyncio.run(create_spotify_podcast())
                results['spotify'] = success
                if success:
                    print("✅ Spotify podcast publikálva")
                else:
                    print("⚠️ Spotify podcast sikertelen")
            except Exception as e:
                print(f"❌ Spotify hiba: {str(e)}")
                results['spotify'] = False
        
        return results
    
    def run_youtube_newscast(self):
        """YouTube híradó készítése (naponta)"""
        print(f"\n📺 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - YOUTUBE NEWSCAST")
        
        if not self.social_enabled['youtube']:
            print("⚠️ YouTube publikálás kikapcsolva")
            return False
        
        try:
            print("🎬 YouTube híradó készítése...")
            success = asyncio.run(create_youtube_newscast())
            if success:
                print("✅ YouTube híradó publikálva")
            else:
                print("⚠️ YouTube híradó sikertelen")
            return success
        except Exception as e:
            print(f"❌ YouTube hiba: {str(e)}")
            return False
    
    async def _emergency_processing(self):
        """Breaking news gyors feldolgozás"""
        print("🚨 EMERGENCY PROCESSING MODE")
        
        # Gyors AI feldolgozás
        self.run_ai_processing()
        await asyncio.sleep(30)
        
        # Gyors TTS
        self.run_tts_generation()
        await asyncio.sleep(30)
        
        # Azonnali Twitter post
        if self.social_enabled['twitter']:
            await create_twitter_thread()
        
        print("🚨 Emergency processing complete")
    
    def run_full_pipeline(self):
        """Teljes pipeline futtatása"""
        print(f"\n🚀 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - FULL PIPELINE START")
        print("=" * 60)
        
        # 1. Hírgyűjtés
        self.run_news_scraping()
        time.sleep(2)
        
        # 2. AI feldolgozás
        self.run_ai_processing()
        time.sleep(2)  # Reduced coordination pause
        
        # 3. TTS generálás
        self.run_tts_generation()
        time.sleep(2)  # Reduced coordination pause
        
        # 4. Social media (ha van új tartalom)
        self.run_social_media_publishing()
        
        print("=" * 60)
        print("🎉 FULL PIPELINE COMPLETE")
    
    def run_morning_operations(self):
        """Reggeli műveletek (6:00)"""
        print(f"\n🌅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - MORNING OPERATIONS")
        
        # Teljes pipeline
        self.run_full_pipeline()
        
        # YouTube híradó
        self.run_youtube_newscast()
        
        print("🌅 Morning operations complete")
    
    def run_evening_operations(self):
        """Esti műveletek (18:00)"""
        print(f"\n🌆 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - EVENING OPERATIONS")
        
        # Teljes pipeline
        self.run_full_pipeline()
        
        # Extra YouTube ha sok hír volt
        current_hour = datetime.now().hour
        if current_hour == 18:  # Csak 18:00-kor
            self.run_youtube_newscast()
        
        print("🌆 Evening operations complete")
    
    def run_cleanup(self):
        """Takarítás futtatása"""
        print(f"\n🗑️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - CLEANUP OPERATIONS")
        try:
            cleanup_old_data()
            print("✅ Cleanup complete")
        except Exception as e:
            print(f"❌ Cleanup hiba: {str(e)}")
    
    def setup_production_schedules(self):
        """Production ütemezések (javasolt beállítás)"""
        print("📅 Production Schedule Setup...")
        
        # === CORE OPERATIONS ===
        # Reggeli teljes pipeline + YouTube (6:00)
        schedule.every().day.at("06:00").do(self.run_morning_operations)
        
        # Esti teljes pipeline + YouTube (18:00)
        schedule.every().day.at("18:00").do(self.run_evening_operations)
        
        # === FREQUENT UPDATES ===
        # Gyors hírgyűjtés minden 30 percben (breaking news)
        schedule.every(30).minutes.do(self.run_news_scraping)
        
        # AI + TTS óránként (friss tartalom)
        schedule.every().hour.at(":15").do(self.run_ai_processing)
        schedule.every().hour.at(":45").do(self.run_tts_generation)
        
        # === SOCIAL MEDIA ===
        # Twitter + Spotify 6 óránként
        schedule.every(6).hours.do(self.run_social_media_publishing)
        
        # === MAINTENANCE ===
        # Cleanup hajnali 3-kor
        schedule.every().day.at("03:00").do(self.run_cleanup)
        
        print("✅ Production schedules configured:")
        print("   🌅 Morning ops: 06:00 (full + YouTube)")
        print("   🌆 Evening ops: 18:00 (full + YouTube)")
        print("   🔍 Scraping: every 30 min")
        print("   🤖 AI/TTS: hourly")
        print("   📱 Social: every 6h")
        print("   🗑️ Cleanup: 03:00")
    
    def setup_development_schedules(self):
        """Development ütemezések (teszteléshez)"""
        print("📅 Development Schedule Setup...")
        
        # Teljes pipeline 2 óránként
        schedule.every(2).hours.do(self.run_full_pipeline)
        
        # Social media tesztelés óránként
        schedule.every().hour.at(":30").do(self.run_social_media_publishing)
        
        # YouTube tesztelés 6 óránként
        schedule.every(6).hours.do(self.run_youtube_newscast)
        
        # Cleanup naponta
        schedule.every().day.at("03:00").do(self.run_cleanup)
        
        print("✅ Development schedules configured")
    
    def start(self, mode="production"):
        """Scheduler indítása"""
        if self.is_running:
            print("⚠️ Scheduler már fut!")
            return
        
        self.is_running = True
        
        # Schedule setup
        if mode == "production":
            self.setup_production_schedules()
        elif mode == "development":
            self.setup_development_schedules()
        else:
            print(f"❌ Ismeretlen mód: {mode}")
            return
        
        print(f"🚀 HírMagnet Advanced Scheduler [{mode.upper()}] elindítva!")
        print(f"🤖 Social Media: {', '.join([k for k, v in self.social_enabled.items() if v])}")
        print("Press Ctrl+C to stop...")
        
        # Indítási teszt (kihagyható production-ban)
        if mode == "development":
            print("\n🎬 Indítási teszt pipeline...")
            self.run_full_pipeline()
        
        # Fő ciklus
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Ellenőrzés percenként
                
        except KeyboardInterrupt:
            print("\n\n🛑 Scheduler leállítása...")
            self.is_running = False
        except Exception as e:
            print(f"\n❌ Scheduler kritikus hiba: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """Scheduler leállítása"""
        self.is_running = False
        schedule.clear()
        print("🛑 Scheduler leállítva")
    
    def status_report(self):
        """Rendszer státusz jelentés"""
        print("\n📊 SYSTEM STATUS REPORT")
        print("=" * 40)
        
        # Database status
        try:
            from database.db import get_db_session
            db = get_db_session()
            
            from database.models import Article, SocialPost
            total_articles = db.query(Article).count()
            processed_articles = db.query(Article).filter(Article.is_processed == True).count()
            audio_articles = db.query(Article).filter(Article.has_audio == True).count()
            social_posts = db.query(SocialPost).count()
            
            print(f"📰 Articles: {total_articles} (processed: {processed_articles}, audio: {audio_articles})")
            print(f"📱 Social Posts: {social_posts}")
            
            db.close()
        except Exception as e:
            print(f"❌ Database status error: {str(e)}")
        
        # Social media status
        print(f"🐦 Twitter: {'✅' if self.social_enabled['twitter'] else '❌'}")
        print(f"🎵 Spotify: {'✅' if self.social_enabled['spotify'] else '❌'}")
        print(f"📺 YouTube: {'✅' if self.social_enabled['youtube'] else '❌'}")
        
        print("=" * 40)

def main():
    """Fő belépési pont"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HírMagnet Advanced Scheduler')
    parser.add_argument('--mode', choices=['production', 'development'], 
                       default='production', help='Scheduler mode')
    parser.add_argument('--status', action='store_true', help='Show status report')
    
    args = parser.parse_args()
    
    scheduler = AdvancedAutomationScheduler()
    
    if args.status:
        scheduler.status_report()
        return
    
    scheduler.start(mode=args.mode)

if __name__ == "__main__":
    main()