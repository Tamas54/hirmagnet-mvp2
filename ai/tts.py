import openai
from openai import OpenAI
from database.db import get_db_session
from database.models import Article, ProcessingLog
from config.settings import OPENAI_API_KEY, TTS_VOICE, TTS_SPEED, AUDIO_DIR
import os
import time
import hashlib

class TTSGenerator:
    def __init__(self):
        # A proxies paramétert nem használjuk az új OpenAI API-val
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Audio könyvtár létrehozása
        os.makedirs(AUDIO_DIR, exist_ok=True)
        
    def generate_audio_for_unprocessed(self):
        """Hangfájl generálás cikkekhez amikhez még nincs"""
        db = get_db_session()
        
        try:
            # Cikkek amelyekhez nincs még hangfájl
            articles_without_audio = db.query(Article).filter(
                Article.is_processed == True,
                Article.has_audio == False
            ).limit(20).all()  # Max 20 audio egyszerre (költség kontroll)
            
            if not articles_without_audio:
                print("✅ Minden cikkhez van hangfájl")
                return 0
            
            generated_count = 0
            start_time = time.time()
            
            for article in articles_without_audio:
                try:
                    print(f"🎵 TTS generálás: {article.title[:50]}...")
                    
                    # Hangfájl generálás
                    audio_filename = self._generate_single_audio(article)
                    
                    if audio_filename:
                        # Adatbázis frissítés
                        article.has_audio = True
                        article.audio_filename = audio_filename
                        article.audio_duration = self._get_audio_duration(audio_filename)
                        
                        db.commit()
                        generated_count += 1
                        
                        print(f"✅ Audio generálva: {audio_filename}")
                    
                    # Rate limiting (OpenAI TTS API)
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ TTS generálási hiba: {str(e)}")
                    db.rollback()
                    continue
            
            processing_time = time.time() - start_time
            
            # Naplózás
            log = ProcessingLog(
                action="tts_generation",
                articles_processed=generated_count,
                success=True,
                processing_time=processing_time
            )
            db.add(log)
            db.commit()
            
            print(f"🎉 TTS generálás kész: {generated_count} hangfájl ({processing_time:.1f}s)")
            return generated_count
            
        except Exception as e:
            print(f"❌ TTS generálási hiba: {str(e)}")
            return 0
        finally:
            db.close()
    
    def _generate_single_audio(self, article: Article):
        """Egy cikkhez hangfájl generálás"""
        try:
            # Szöveg előkészítése
            text_to_speak = self._prepare_text_for_tts(article)
            
            if not text_to_speak or len(text_to_speak) < 10:
                print(f"⚠️ Túl rövid szöveg TTS-hez")
                return None
            
            # Hangfájl név generálás
            text_hash = hashlib.md5(text_to_speak.encode()).hexdigest()[:8]
            audio_filename = f"article_{article.id}_{text_hash}.mp3"
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            
            # Ha már létezik, skip
            if os.path.exists(audio_path):
                return audio_filename
            
            # OpenAI TTS API hívás
            response = self.client.audio.speech.create(
                model="tts-1",  # tts-1 vagy tts-1-hd (drágább de jobb minőség)
                voice=TTS_VOICE,
                input=text_to_speak,
                speed=TTS_SPEED
            )
            
            # Hangfájl mentése
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            return audio_filename
            
        except Exception as e:
            print(f"OpenAI TTS hiba: {str(e)}")
            return None
    
    def _prepare_text_for_tts(self, article: Article):
        """Szöveg előkészítése TTS-hez"""
        
        # Ha van AI összefoglaló, azt használjuk
        if article.ai_summary:
            text = f"{article.ai_title or article.title}. {article.ai_summary}"
        else:
            # Fallback az eredeti tartalommal
            text = f"{article.title}. {article.original_content[:500] if article.original_content else ''}"
        
        # Szöveg tisztítás TTS-hez
        text = text.replace("&quot;", '"')
        text = text.replace("&amp;", "és")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        
        # Maximum hossz (OpenAI TTS limit: 4096 karakter)
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        return text.strip()
    
    def _get_audio_duration(self, filename):
        """Hangfájl hosszának meghatározása (egyszerű becslés)"""
        try:
            audio_path = os.path.join(AUDIO_DIR, filename)
            file_size = os.path.getsize(audio_path)
            
            # Durva becslés: ~1KB = 1 másodperc MP3-nál
            estimated_duration = file_size / 1000
            
            return round(estimated_duration, 1)
        except:
            return 0.0
    
    def cleanup_old_audio_files(self, days_old=7):
        """Régi hangfájlok törlése (tárhely megtakarítás)"""
        try:
            current_time = time.time()
            deleted_count = 0
            
            for filename in os.listdir(AUDIO_DIR):
                if not filename.endswith('.mp3'):
                    continue
                    
                file_path = os.path.join(AUDIO_DIR, filename)
                file_age = current_time - os.path.getctime(file_path)
                
                # Ha régebbi mint X nap
                if file_age > (days_old * 24 * 3600):
                    os.remove(file_path)
                    deleted_count += 1
            
            print(f"🗑️ {deleted_count} régi hangfájl törölve")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Cleanup hiba: {str(e)}")
            return 0

def main():
    """Fő TTS generálás (cron job-hoz)"""
    tts = TTSGenerator()
    try:
        generated = tts.generate_audio_for_unprocessed()
        print(f"✅ TTS generálás kész: {generated} hangfájl")
        return generated
    except Exception as e:
        print(f"❌ TTS generálási hiba: {str(e)}")
        return 0

if __name__ == "__main__":
    main()