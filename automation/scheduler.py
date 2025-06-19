import schedule
import time
import sys
import os
from datetime import datetime

# Projekt gyökér könyvtár hozzáadása a sys.path-hoz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.news_scraper import NewsScraper
from ai.processor import AIProcessor
from ai.tts import TTSGenerator
from automation.cleanup import cleanup_old_data

class AutomationScheduler:
    def __init__(self):
        self.scraper = NewsScraper()
        self.ai_processor = AIProcessor()
        self.tts_generator = TTSGenerator()
        self.is_running = False
        
    def run_news_scraping(self):
        """Hírgyűjtés futtatása"""
        print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Hírgyűjtés indítása")
        try:
            new_articles = self.scraper.scrape_all_sources()
            print(f"✅ Hírgyűjtés befejezve: {new_articles} új cikk")
        except Exception as e:
            print(f"❌ Hírgyűjtési hiba: {str(e)}")
    
    def run_ai_processing(self):
        """AI feldolgozás futtatása"""
        print(f"\n🤖 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - AI feldolgozás indítása")
        try:
            processed = self.ai_processor.process_unprocessed_articles()
            print(f"✅ AI feldolgozás befejezve: {processed} cikk")
        except Exception as e:
            print(f"❌ AI feldolgozási hiba: {str(e)}")
    
    def run_tts_generation(self):
        """TTS generálás futtatása"""
        print(f"\n🎵 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - TTS generálás indítása")
        try:
            generated = self.tts_generator.generate_audio_for_unprocessed()
            print(f"✅ TTS generálás befejezve: {generated} hangfájl")
        except Exception as e:
            print(f"❌ TTS generálási hiba: {str(e)}")
    
    def run_cleanup(self):
        """Takarítás futtatása"""
        print(f"\n🗑️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Cleanup indítása")
        try:
            cleanup_old_data()
            print("✅ Cleanup befejezve")
        except Exception as e:
            print(f"❌ Cleanup hiba: {str(e)}")
    
    def run_full_pipeline(self):
        """Teljes pipeline futtatása (scraping -> AI -> TTS)"""
        print(f"\n🚀 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Teljes pipeline indítása")
        
        # 1. Hírgyűjtés
        self.run_news_scraping()
        time.sleep(30)  # 30 sec szünet
        
        # 2. AI feldolgozás
        self.run_ai_processing()
        time.sleep(30)  # 30 sec szünet
        
        # 3. TTS generálás
        self.run_tts_generation()
        
        print("🎉 Teljes pipeline befejezve!")
    
    def setup_schedules(self):
        """Ütemezések beállítása"""
        
        # ========== PRODUCTION SCHEDULE ==========
        
        # Teljes pipeline óránként (fő folyamat)
        schedule.every().hour.at(":05").do(self.run_full_pipeline)
        
        # Gyors hírgyűjtés 30 percenként (breaking news-hez)
        schedule.every(30).minutes.do(self.run_news_scraping)
        
        # AI feldolgozás 20 percenként (ha van feldolgozatlan)
        schedule.every(20).minutes.do(self.run_ai_processing)
        
        # TTS generálás 15 percenként (ha van új AI cikk)
        schedule.every(15).minutes.do(self.run_tts_generation)
        
        # Napi cleanup hajnali 3-kor
        schedule.every().day.at("03:00").do(self.run_cleanup)
        
        # ========== ALTERNATÍV: EGYSZERŰBB SCHEDULE ==========
        # Ha túl gyakori lenne, használd ezt:
        
        # # Teljes pipeline 2 óránként
        # schedule.every(2).hours.do(self.run_full_pipeline)
        
        # # Napi cleanup hajnali 3-kor
        # schedule.every().day.at("03:00").do(self.run_cleanup)
        
        print("📅 Ütemezések beállítva:")
        print("   - Teljes pipeline: óránként")
        print("   - Hírgyűjtés: 30 percenként")
        print("   - AI feldolgozás: 20 percenként") 
        print("   - TTS generálás: 15 percenként")
        print("   - Cleanup: naponta hajnali 3-kor")
    
    def start(self):
        """Scheduler indítása"""
        if self.is_running:
            print("⚠️ Scheduler már fut!")
            return
        
        self.is_running = True
        self.setup_schedules()
        
        print("🚀 HírMagnet Automation Scheduler elindítva!")
        print("Press Ctrl+C to stop...")
        
        # Azonnal futtatunk egyet indításkor
        print("\n🎬 Indítási pipeline futtatása...")
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
            print(f"\n❌ Scheduler hiba: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """Scheduler leállítása"""
        self.is_running = False
        print("🛑 Scheduler leállítva")

def main():
    """Fő belépési pont"""
    scheduler = AutomationScheduler()
    scheduler.start()

if __name__ == "__main__":
    main()