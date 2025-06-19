#!/usr/bin/env python3
"""
hirmagnet_newspaper.py - ÚJSÁG RENDSZER
======================================
🗞️ EGYETLEN SCRIPT - MINDEN BENNE
🚀 python hirmagnet_newspaper.py
💻 Honlap: http://localhost:8000
🔄 Automatikus frissítés: 30 percenként
"""

import os
import sys
import time
import threading
import subprocess
import asyncio
import signal
from datetime import datetime
import webbrowser

class HirMagnetNewspaper:
    def __init__(self):
        self.running = True
        self.frontend_ready = False
        self.articles_generated = 0
        self.cycles_completed = 0
        self.start_time = datetime.now()
        
        print("🗞️ HÍRMAGNET ÚJSÁG RENDSZER")
        print("=" * 40)
        print("🚀 Indítás...")
        
        # Signal handler
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def shutdown(self, signum=None, frame=None):
        """Leállítás"""
        print("\n🛑 Újság leállítása...")
        self.running = False
        sys.exit(0)
    
    def start_frontend(self):
        """Frontend elindítása"""
        print("🌐 Honlap indítása...")
        
        def run_server():
            try:
                import uvicorn
                from api.main import app
                uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
            except Exception as e:
                print(f"❌ Frontend hiba: {e}")
        
        frontend_thread = threading.Thread(target=run_server, daemon=True)
        frontend_thread.start()
        
        # Várj hogy beinduljon
        time.sleep(5)
        
        # Test
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.frontend_ready = True
                print("✅ Honlap elérhető: http://localhost:8000")
                return True
        except:
            pass
        
        print("⚠️ Frontend lehet hogy nem válaszol még")
        return True
    
    def generate_content(self):
        """Cikkek generálása"""
        print(f"\n📝 Cikkírás #{self.cycles_completed + 1}...")
        
        try:
            cmd = [sys.executable, "test_master.py", "--mode", "quick", "--generate-content"]
            
            #DEBUK INFO
            print(f"🔧 COMMAND: {' '.join(cmd)}")
            print(f"🔧 Working dir: {os.getcwd()}")
            print(f"🔧 Python executable: {sys.executable}")
            print(f"🔧 Current time: {datetime.now()}")
            
            # FIXED: Pass environment variables to subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=os.environ)
            
            # DETALJEZETT DEBUG
            print(f"🔧 RETURN CODE: {result.returncode}")
            print(f"🔧 STDOUT LENGTH: {len(result.stdout)} chars")
            print(f"🔧 STDERR LENGTH: {len(result.stderr)} chars")
            
            if result.stdout:
                print(f"🔧 STDOUT (first 1000 chars):")
                print("=" * 50)
                print(result.stdout[:1000])
                print("=" * 50)
            
            if result.stderr:
                print(f"🔧 STDERR (full):")
                print("!" * 50)
                print(result.stderr)
                print("!" * 50)
            
            if result.returncode == 0:
                # Count articles
                import re
                output = result.stdout
                
                # Többféle pattern keresése
                patterns = [
                    r'(\d+).*?új cikk',
                    r'(\d+).*?articles?.*?processed',
                    r'(\d+).*?cikk.*?elkészült',
                    r'✅.*?(\d+).*?cikk',
                    r'CIKK.*?(\d+)',
                    r'feldolgozott.*?(\d+)',
                    r'generált.*?(\d+)'
                ]
                
                found_counts = []
                for pattern in patterns:
                    matches = re.findall(pattern, output, re.IGNORECASE)
                    if matches:
                        found_counts.extend([int(m) for m in matches])
                
                print(f"🔧 FOUND COUNTS: {found_counts}")
                
                if found_counts:
                    count = max(found_counts)  # Take the highest number found
                    self.articles_generated += count
                    print(f"✅ {count} új cikk elkészült")
                else:
                    print("⚠️ Nem találtam cikk számot az outputban")
                    print("✅ Cikkírás befejezve (ismeretlen számmal)")
                
                self.cycles_completed += 1
                return True
            else:
                print(f"❌ SUBPROCESS FAILED!")
                print(f"❌ Return code: {result.returncode}")
                if result.stderr:
                    print(f"❌ Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Cikkírás túl hosszú (15 perc)")
            return False
        except Exception as e:
            print(f"❌ Váratlan hiba: {e}")
            import traceback
            print(f"🔧 TRACEBACK: {traceback.format_exc()}")
            return False
    
    def content_generation_loop(self):
        """Folyamatos cikkírás háttérben"""
        print("🔄 Automatikus cikkírás indítva...")
        
        while self.running:
            try:
                # Első cikk azonnal
                if self.cycles_completed == 0:
                    self.generate_content()
                
                # Várj 30 percet
                for i in range(1800):  # 30 * 60 = 1800 másodperc
                    if not self.running:
                        return
                    time.sleep(1)
                
                # Generate content
                if self.running:
                    self.generate_content()
                    
            except Exception as e:
                print(f"❌ Háttér hiba: {e}")
                time.sleep(60)
    
    def status_display_loop(self):
        """Státusz kijelzés"""
        while self.running:
            try:
                time.sleep(300)  # 5 percenként
                if self.running:
                    uptime = datetime.now() - self.start_time
                    print(f"\n📊 ÚJSÁG STÁTUSZ:")
                    print(f"   ⏱️ Üzemidő: {uptime}")
                    print(f"   📝 Cikkírási ciklusok: {self.cycles_completed}")
                    print(f"   📰 Generált cikkek: {self.articles_generated}")
                    print(f"   🌐 Honlap: {'✅ Működik' if self.frontend_ready else '❌ Probléma'}")
                    print(f"   🔗 http://localhost:8000")
            except:
                pass
    
    def open_browser(self):
        """Browser megnyitása"""
        try:
            time.sleep(3)
            webbrowser.open("http://localhost:8000")
            print("🌐 Browser megnyitva")
        except:
            print("⚠️ Browser megnyitás sikertelen")
    
    def run(self):
        """Újság indítása"""
        try:
            # Check environment
            if not os.path.exists("test_master.py"):
                print("❌ Nem HírMagnet mappában vagy!")
                return False
            
            # Start frontend
            if not self.start_frontend():
                print("❌ Frontend indítás sikertelen")
                return False
            
            # Open browser
            browser_thread = threading.Thread(target=self.open_browser, daemon=True)
            browser_thread.start()
            
            # Start content generation loop
            content_thread = threading.Thread(target=self.content_generation_loop, daemon=True)
            content_thread.start()
            
            # Start status display
            status_thread = threading.Thread(target=self.status_display_loop, daemon=True)
            status_thread.start()
            
            # Show startup info
            print("\n🎉 HÍRMAGNET ÚJSÁG ELINDULT!")
            print("=" * 40)
            print("🌐 Honlap: http://localhost:8000")
            print("📝 Automatikus cikkírás: 30 percenként")
            print("📊 Státusz: 5 percenként")
            print("🛑 Leállítás: Ctrl+C")
            print("=" * 40)
            
            # Main loop - keep alive
            while self.running:
                time.sleep(1)
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Felhasználó leállította")
            return True
        except Exception as e:
            print(f"\n❌ Kritikus hiba: {e}")
            return False

def main():
    """Főprogram"""
    print("🗞️ HÍRMAGNET ÚJSÁG")
    print("==================")
    
    # Quick check
    try:
        import fastapi, uvicorn, requests
    except ImportError as e:
        print(f"❌ Hiányzó csomag: {e}")
        print("💡 Telepítsd: pip install fastapi uvicorn requests")
        return 1
    
    # Virtual env check
    if os.path.exists("venv") and not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ Virtual environment nincs bekapcsolva!")
        print("💡 Futtasd: source venv/bin/activate")
        print("💡 Vagy: venv/bin/python hirmagnet_newspaper.py")
    
    # Start newspaper
    newspaper = HirMagnetNewspaper()
    success = newspaper.run()
    
    if success:
        print("\n👋 Újság leállítva!")
    else:
        print("\n💥 Újság hibával állt le!")
        return 1
    
    return 0

def content_generation_background():
    """Background content generation for production - RENDER OPTIMIZED"""
    import time
    import asyncio
    print("🔄 Content generation loop started...")
    
    while True:
        try:
            print("📝 Starting content generation cycle...")
            
            # RENDER FIX: Try direct import approach first, fallback to subprocess
            try:
                print("🔧 RENDER APPROACH 1: Direct import method")
                # Import test_master directly and call its function
                import sys
                sys.path.append(os.getcwd())
                from test_master import run_master_test
                
                # Run content generation directly
                print("🔧 Running direct content generation...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(run_master_test("quick", False, True))
                loop.close()
                print("✅ Direct content generation completed successfully")
                
            except Exception as direct_error:
                print(f"🔧 RENDER APPROACH 1 FAILED: {direct_error}")
                print("🔧 RENDER APPROACH 2: Subprocess method")
                
                # Fallback to subprocess with enhanced debugging
                import subprocess
                import sys
                
                cmd = [sys.executable, "test_master.py", "--mode", "quick", "--generate-content"]
                print(f"🔧 RENDER DEBUG - Command: {' '.join(cmd)}")
                print(f"🔧 RENDER DEBUG - Working dir: {os.getcwd()}")
                print(f"🔧 RENDER DEBUG - Python path: {sys.executable}")
                
                # Check if test_master.py exists
                if os.path.exists("test_master.py"):
                    print("🔧 RENDER DEBUG - test_master.py exists")
                else:
                    print("❌ RENDER DEBUG - test_master.py NOT FOUND!")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=os.environ)
                
                # RENDER FIX: Comprehensive error reporting
                print(f"🔧 RENDER DEBUG - Return code: {result.returncode}")
                print(f"🔧 RENDER DEBUG - Stdout length: {len(result.stdout)} chars")
                print(f"🔧 RENDER DEBUG - Stderr length: {len(result.stderr)} chars")
                
                if result.stdout:
                    print(f"🔧 RENDER DEBUG - Stdout (first 2000 chars):")
                    print(result.stdout[:2000])
                
                if result.stderr:
                    print(f"🔧 RENDER DEBUG - Stderr (full):")
                    print(result.stderr)
                
                if result.returncode == 0:
                    print("✅ Subprocess content generation completed successfully")
                else:
                    print(f"❌ Content generation failed with return code: {result.returncode}")
                    print(f"❌ Error details: {result.stderr}")
            
            # Várj 30 percet
            print("⏰ Waiting 30 minutes for next cycle...")
            time.sleep(1800)  # 30 * 60 = 1800 seconds
            
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            time.sleep(300)  # 5 perc várakozás hiba esetén

if __name__ == "__main__":
    if os.environ.get("RENDER"):
        # RENDER PRODUCTION MODE - FastAPI + Content Generation
        print("🚀 HírMagnet RENDER Production Mode")
        print("📱 FastAPI server + Background content generation")
        
        port = int(os.environ.get("PORT", 8000))
        
        # Background content generation indítása
        content_thread = threading.Thread(target=content_generation_background, daemon=True)
        content_thread.start()
        print("✅ Background content generation started")
        
        # FastAPI indítása
        import uvicorn
        from api.main import app
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    else:
        # DEVELOPMENT MODE - teljes funkcionalitás
        print("🔧 Development mode - Full functionality")
        sys.exit(main())