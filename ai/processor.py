# ai/processor.py - v5.0 - OPERATION BEFEHLSKETTE + FEUERLEITANLAGE
# Letisztult, végrehajtásra fókuszáló modul megerősített diagnosztikai képességekkel

# .env fájl betöltése ELSŐ lépésként
from dotenv import load_dotenv
load_dotenv()

import openai
from openai import OpenAI
import google.generativeai as genai
from database.db import get_db_session
from database.models import Article, ProcessingLog
from config.settings import OPENAI_API_KEY
from config.sources import is_fast_lane_source # Csak a fast-lane ellenőrzés maradt
import time
import re
import json
import os
import traceback  # Új import a részletes hibakövetéshez
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

# A hadtest többi egységének importálása
try:
    from ai.prompt_manager import get_prompt_manager
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False

try:
    from ai.journalists import get_journalist_manager
    JOURNALIST_MANAGER_AVAILABLE = True
except ImportError:
    JOURNALIST_MANAGER_AVAILABLE = False

class StrategicDualPhaseAIProcessor:
    """
    🧲 HIRMAGNET STRATEGIC AI PROCESSOR v5.0 - BEFEHLSKETTE + FEUERLEITANLAGE
    
    VÉGSŐ JELLEMZŐK:
    ✅ Letisztult felelősségi kör: Kizárólag a tartalom-generálás vezénylése.
    ✅ Nincs több belső kategorizálás vagy pontozás.
    ✅ Tökéletes szinkronban működik az `editorial_ai.py` v5.0 modullal.
    ✅ Ésszerű GPT-4o routing és újságíró-kiosztás a kapott adatok alapján.
    ✅ Backward compatibility a jelenlegi rendszerrel.
    ✅ Enhanced Error Logging and Diagnostics.
    """
    
    def __init__(self):
        print("🧲 Initializing AI Processor v5.0 (BEFEHLSKETTE + FEUERLEITANLAGE)...")
        
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
            print("✅ Gemini 2.5 Flash connected")
        else:
            self.gemini_model = None
            print("⚠️ GEMINI_API_KEY missing!")
        
        self.prompt_manager = get_prompt_manager() if PROMPT_MANAGER_AVAILABLE else None
        self.journalist_manager = get_journalist_manager() if JOURNALIST_MANAGER_AVAILABLE else None
        
        # A routing küszöbök megmaradnak, mert a kapott pontszám alapján itt dől el a modellválasztás
        self.routing_thresholds = {
            "critical": 16,    # 16+ = GPT-4o guaranteed
            "important": 14,   # 14-15 = GPT-4o if quota available
            "standard": 12     # 12-13 = GPT-4o if quota available
        }
        
        self.daily_premium_count = 0
        self.daily_premium_limit = 15
        
        # Session statistics
        self.session_stats = defaultdict(int)
        
        print("🎯 AI Processor v5.0 ready for final deployment with enhanced diagnostics!")
        
    def process_articles_for_generation(self, articles: List[Article]) -> int:
        """
        FŐ FUNKCIÓ v5.0: Az elő-feldolgozott és szűrt cikkek átvétele és a tartalom-generálás elindítása.
        
        Az editorial_ai.py v5.0 már elvégezte:
        - Kategorizálást
        - Fontosság-pontozást  
        - Duplikátum-szűrést
        
        Itt csak a végleges tartalom-generálás történik.
        """
        db = get_db_session()
        try:
            self._reset_daily_counter_if_needed()
            if self.journalist_manager:
                self.journalist_manager.reset_daily_usage_if_needed()

            if not articles:
                print("✅ Nincs tartalom-generálásra kijelölt cikk.")
                return 0
            
            print(f"\n✍️ CONTENT GENERATION v5.0 STARTED: {len(articles)} articles")
            print(f"💎 Premium quota: {self.daily_premium_count}/{self.daily_premium_limit}")
            
            processed_count = 0
            start_time = time.time()
            
            for i, article in enumerate(articles):
                try:
                    print(f"\n🎯 Processing {i+1}/{len(articles)}: {article.original_title[:50]}...")
                    
                    # A cikk már rendelkezik a `category` és `importance_score` attribútumokkal az editorial_ai-tól.
                    importance_score = getattr(article, 'importance_score', 8)
                    category = getattr(article, 'category', 'general')
                    
                    print(f"   📊 Category: {category}, Importance: {importance_score}/20")
                    
                    # Újságíró kijelölés
                    journalist_assignment = None
                    if self.journalist_manager:
                        journalist_assignment = self.journalist_manager.select_journalist_for_article(
                            category, importance_score, article.original_content or ""
                        )
                        
                        if journalist_assignment:
                            print(f"   👤 Journalist: {journalist_assignment['journalist_name']}")
                            self.session_stats['journalist_assignments'] += 1
                    
                    # Model meghatározás
                    model_to_use = self._determine_model(importance_score, journalist_assignment)
                    print(f"   🤖 Model: {model_to_use.upper()}")
                    
                    # Tartalom generálás
                    ai_result = self._generate_final_content(article, model_to_use, journalist_assignment)

                    # Adatbázis frissítése a végleges tartalommal
                    article.ai_summary = ai_result.get('article_body', ai_result.get('summary'))
                    article.ai_title = ai_result.get('title')
                    article.sentiment = ai_result.get('sentiment')
                    article.seo_keywords = ai_result.get('keywords')
                    article.is_processed = True # A cikk feldolgozása befejeződött
                    article.processing_model = f"befehlskette_v5.0_{model_to_use}"
                    
                    if journalist_assignment:
                        article.assigned_journalist = journalist_assignment.get('journalist_id')
                        article.journalist_name = journalist_assignment.get('journalist_name')

                    db.merge(article)
                    db.commit()
                    processed_count += 1
                    
                    # Stats tracking
                    if model_to_use == 'gpt4o':
                        self.session_stats['gpt4o_used'] += 1
                    else:
                        self.session_stats['gemini_used'] += 1
                    
                    print(f"   ✅ Content generated successfully")
                    
                    # Rate limiting
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"   ❌ Critical error in main processing loop (Article ID: {article.id}):")
                    print(f"      - Error Type: {type(e).__name__}")
                    print(f"      - Detailed Message: {str(e)}")
                    print(f"      - Traceback: \n{traceback.format_exc()}")
                    db.rollback()
                    self.session_stats['generation_errors'] += 1
                    continue
            
            # Session cleanup
            if self.journalist_manager: 
                self.journalist_manager.save_daily_usage()
            self._save_daily_counter()
            
            processing_time = time.time() - start_time
            self._print_generation_report(processed_count, processing_time)
            
            # Log the session
            log = ProcessingLog(
                action="content_generation_v5.0_befehlskette_feuerleitanlage",
                articles_processed=processed_count,
                success=True,
                processing_time=processing_time,
                error_message=self._create_session_summary()
            )
            db.add(log)
            db.commit()
            
            return processed_count
            
        finally:
            db.close()

    def _determine_model(self, importance_score: int, journalist_assignment: Dict = None) -> str:
        """Meghatározza a használandó modellt a kapott pontszám alapján."""
        
        # Priority 1: Journalist preference
        if journalist_assignment and journalist_assignment.get('preferred_model') == 'gpt4o':
            if self.daily_premium_count < self.daily_premium_limit:
                self.daily_premium_count += 1
                return 'gpt4o'
            else:
                print(f"   ⚠️ Journalist requested GPT-4o but quota exceeded, using Gemini")
                return 'gemini'
        
        # Priority 2: Importance-based routing
        if importance_score >= self.routing_thresholds["critical"]:  # 16+
            if self.daily_premium_count < self.daily_premium_limit:
                self.daily_premium_count += 1
                return 'gpt4o'
            else:
                print(f"   ⚠️ Critical article but quota exceeded, using Gemini")
                return 'gemini'
                
        elif importance_score >= self.routing_thresholds["important"]:  # 14-15
            if self.daily_premium_count < self.daily_premium_limit * 0.8:  # 80% quota threshold
                self.daily_premium_count += 1
                return 'gpt4o'
            else:
                return 'gemini'
                
        elif importance_score >= self.routing_thresholds["standard"]:  # 12-13
            if self.daily_premium_count < self.daily_premium_limit * 0.6:  # 60% quota threshold
                self.daily_premium_count += 1
                return 'gpt4o'
            else:
                return 'gemini'
        
        # Default: Gemini for lower importance
        return 'gemini'

    def _generate_final_content(self, article: Article, model_to_use: str, journalist_assignment: Dict = None) -> Dict[str, Any]:
        """A tartalom-generálás központi logikája."""
        
        if journalist_assignment:
            return self._generate_with_journalist(article, journalist_assignment, model_to_use)
        else:
            return self._generate_standard_content(article, model_to_use)

    def _generate_with_journalist(self, article: Article, journalist_assignment: Dict, model: str) -> Dict[str, Any]:
        """Tartalom generálása a kijelölt újságíró promptjával - Enhanced Error Logging."""
        clean_content = self._clean_content(article.original_content or "")
        
        if not self.journalist_manager:
            return self._generate_fallback_content(article)
        
        prompt = self.journalist_manager.get_journalist_prompt(
            journalist_assignment['journalist_id'],
            title=article.original_title,
            category=getattr(article, 'category', 'general'),
            importance_score=getattr(article, 'importance_score', 8),
            content=clean_content,
            model=model
        )
        
        if not prompt: 
            print("   ⚠️ Journalist prompt not found, using fallback")
            return self._generate_fallback_content(article)

        try:
            if model == 'gpt4o':
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"Te {journalist_assignment['journalist_name']} vagy, a HírMagnet tapasztalt újságírója."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000, 
                    temperature=0.6
                )
                result_text = response.choices[0].message.content.strip()
            else: # Gemini
                response = self.gemini_model.generate_content(prompt)
                result_text = response.text.strip()
            
            result = self._robust_json_parse(result_text)
            
            # Ensure we have the required fields
            if not result.get('article_body') and not result.get('summary'):
                result['article_body'] = clean_content[:800] + "..."
            if not result.get('title'):
                result['title'] = article.original_title
            if not result.get('sentiment'):
                result['sentiment'] = 'neutral'
            if not result.get('keywords'):
                result['keywords'] = f"{article.source}, hírek, {getattr(article, 'category', 'general')}"
            
            # Add journalist signature
            content = result.get('article_body', result.get('summary', ''))
            if content and journalist_assignment.get('journalist_name'):
                content += f"\n\n--- {journalist_assignment['journalist_name']}, HírMagnet ---"
                result['article_body'] = content
                result['summary'] = content
            
            return result
            
        except Exception as e:
            print(f"❌ Kritikus hiba az '{journalist_assignment['journalist_name']}' generálása során (ID: {article.id}):")
            print(f"   - Hiba Típusa: {type(e).__name__}")
            print(f"   - Részletes Hibaüzenet: {str(e)}")
            print(f"   - Traceback: \n{traceback.format_exc()}")
            return self._generate_fallback_content(article)

    def _generate_standard_content(self, article: Article, model: str) -> Dict[str, Any]:
        """Standard tartalom generálás újságíró nélkül - Enhanced Error Logging."""
        clean_content = self._clean_content(article.original_content or "")
        
        if self.prompt_manager:
            if model == 'gpt4o':
                prompt = self.prompt_manager.get_prompt(
                    "gpt4o_generation",
                    title=article.original_title,
                    category=getattr(article, 'category', 'general'),
                    importance_score=getattr(article, 'importance_score', 8),
                    content=clean_content
                )
            else:
                prompt = self.prompt_manager.get_prompt(
                    "gemini_generation",
                    title=article.original_title,
                    category=getattr(article, 'category', 'general'),
                    content=clean_content
                )
        else:
            prompt = self._get_fallback_prompt(article, model, clean_content)
        
        try:
            if model == 'gpt4o':
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Te egy tapasztalt magyar újságíró vagy."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=3000,
                    temperature=0.4
                )
                result_text = response.choices[0].message.content.strip()
            else:
                response = self.gemini_model.generate_content(prompt)
                result_text = response.text.strip()
            
            result = self._robust_json_parse(result_text)
            
            # Ensure required fields
            if not result.get('article_body') and not result.get('summary'):
                result['article_body'] = clean_content[:600] + "..."
            if not result.get('title'):
                result['title'] = article.original_title
            if not result.get('sentiment'):
                result['sentiment'] = 'neutral'
            if not result.get('keywords'):
                result['keywords'] = f"{article.source}, hírek"
            
            return result
            
        except Exception as e:
            if model == 'gpt4o':
                print(f"❌ Kritikus hiba a standard GPT-4o generálás során (ID: {article.id}):")
            else:
                print(f"❌ Kritikus hiba a standard Gemini generálás során (ID: {article.id}):")
            print(f"   - Hiba Típusa: {type(e).__name__}")
            print(f"   - Részletes Hibaüzenet: {str(e)}")
            print(f"   - Traceback: \n{traceback.format_exc()}")
            return self._generate_fallback_content(article)

    def _generate_fallback_content(self, article: Article) -> Dict[str, Any]:
        """AI-alapú fallback tartalom generálás minimum 400-600 szóval magyar nyelven."""
        clean_content = self._clean_content(article.original_content or "")
        
        # Load fallback prompt
        fallback_prompt_path = "ai/prompts/processing/fallback_content_generation.txt"
        try:
            with open(fallback_prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            prompt = prompt_template.format(
                title=article.original_title,
                category=getattr(article, 'category', 'general'),
                source=article.source,
                content=clean_content
            )
            
            # Generate with Gemini (fallback should use fastest model)
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            result = self._robust_json_parse(result_text)
            
            # Ensure required fields
            if not result.get('article_body'):
                result['article_body'] = self._create_emergency_fallback(article, clean_content)
            if not result.get('title'):
                result['title'] = article.original_title
            if not result.get('sentiment'):
                result['sentiment'] = 'neutral'
            if not result.get('keywords'):
                result['keywords'] = f"{article.source}, hírek, {getattr(article, 'category', 'general')}"
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ AI fallback failed, using emergency fallback: {str(e)}")
            return self._create_emergency_fallback(article, clean_content)
    
    def _create_emergency_fallback(self, article: Article, clean_content: str) -> Dict[str, Any]:
        """Végső vészhelyzeti fallback - Gemini 2.5-tel próbálkozik egyszerű prompttal."""
        
        # Try one more time with Gemini and very simple prompt
        simple_prompt = f"""
        Írj egy 400-600 szavas magyar cikket:
        
        Cím: {article.original_title}
        Forrás: {article.source}
        Tartalom: {clean_content}
        
        KRITIKUS: Csak magyar nyelven írj! Minimum 400 szó!
        
        JSON válasz:
        {{
            "article_body": "400-600 szavas magyar cikk...",
            "title": "magyar cím",
            "sentiment": "neutral",
            "keywords": "kulcsszó1, kulcsszó2"
        }}
        """
        
        try:
            response = self.gemini_model.generate_content(simple_prompt)
            result_text = response.text.strip()
            result = self._robust_json_parse(result_text)
            
            if result.get('article_body') and len(result['article_body']) > 200:
                return result
            else:
                raise Exception("Gemini response too short")
                
        except Exception as e:
            print(f"   ⚠️ Emergency Gemini fallback also failed: {str(e)}")
            # Absolute last resort - hardcoded Hungarian content
            base_content = f"""
            {article.original_title}

            A HírMagnet szerkesztősége szerint fontos fejlemények történtek, amelyek figyelmet érdemelnek a magyar olvasók körében.

            {clean_content[:800] if clean_content else 'A részletek jelenleg tisztázás alatt állnak, de a szerkesztőségünk folyamatosan követi az eseményeket.'}

            Az üggyel kapcsolatos további információk várhatóan hamarosan napvilágot látnak. A helyzet alakulását szerkesztőségünk folyamatosan figyelemmel kísérje, és minden fontos fejleményről beszámolunk olvasóinknak.

            A történtek jelentősége nem elhanyagolható, és várhatóan további reakciókat válthat ki a szakmai és társadalmi körökben egyaránt. A témával kapcsolatos elemzések és szakértői vélemények a következő napokban kerülhetnek nyilvánosságra.

            Forrás: {article.source}
            
            További frissítések és részletes beszámolók hamarosan követik a HírMagnet oldalán.
            """
            
            return {
                'summary': base_content.strip(),
                'article_body': base_content.strip(),
                'title': article.original_title,
                'sentiment': 'neutral',
                'keywords': f"{article.source}, hírek, {getattr(article, 'category', 'general')}, magyarország"
            }

    def _robust_json_parse(self, text: str) -> Dict[str, Any]:
        """Robusztus JSON-értelmező a modellek válaszaihoz."""
        try:
            # First try: Direct JSON parsing
            if text.strip().startswith('{') and text.strip().endswith('}'):
                return json.loads(text.strip())
            
            # Second try: Find JSON in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
        except json.JSONDecodeError:
            pass
        
        # Third try: Regex extraction
        try:
            result = {}
            
            # Extract article_body or summary
            body_match = re.search(r'"(?:article_body|summary)":\s*"([^"]*(?:\\.[^"]*)*)"', text, re.DOTALL)
            if body_match:
                result['article_body'] = body_match.group(1).replace('\\"', '"')
                result['summary'] = result['article_body']
            
            # Extract title
            title_match = re.search(r'"title":\s*"([^"]*(?:\\.[^"]*)*)"', text)
            if title_match:
                result['title'] = title_match.group(1).replace('\\"', '"')
            
            # Extract sentiment
            sentiment_match = re.search(r'"sentiment":\s*"([^"]+)"', text)
            if sentiment_match:
                result['sentiment'] = sentiment_match.group(1)
            
            # Extract keywords
            keywords_match = re.search(r'"keywords":\s*"([^"]*(?:\\.[^"]*)*)"', text)
            if keywords_match:
                result['keywords'] = keywords_match.group(1).replace('\\"', '"')
            
            return result if result else {}
            
        except Exception:
            return {}

    def _clean_content(self, html_content: str) -> str:
        """HTML címkék eltávolítása."""
        if not html_content: 
            return ""
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html_content)
        # Clean whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean

    def _reset_daily_counter_if_needed(self):
        """Napi számláló reset ha új nap"""
        current_date = datetime.now().date()
        
        counter_file = "data/daily_premium_counter.txt"
        
        try:
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    stored_date, stored_count = f.read().strip().split(',')
                    
                if stored_date == str(current_date):
                    self.daily_premium_count = int(stored_count)
                else:
                    self.daily_premium_count = 0
            else:
                self.daily_premium_count = 0
                
        except:
            self.daily_premium_count = 0
    
    def _save_daily_counter(self):
        """Napi számláló mentése"""
        counter_file = "data/daily_premium_counter.txt"
        current_date = datetime.now().date()
        
        try:
            os.makedirs("data", exist_ok=True)
            with open(counter_file, 'w') as f:
                f.write(f"{current_date},{self.daily_premium_count}")
        except:
            pass

    def _create_session_summary(self) -> str:
        """Create session summary for logging"""
        return f"Gemini: {self.session_stats['gemini_used']}, GPT-4o: {self.session_stats['gpt4o_used']}, Journalists: {self.session_stats['journalist_assignments']}, Errors: {self.session_stats['generation_errors']}"

    def _print_generation_report(self, processed_count: int, processing_time: float):
        """Print generation session report"""
        print(f"\n🎉 CONTENT GENERATION v5.0 COMPLETE!")
        print(f"⏱️ Processing time: {processing_time:.1f}s")
        print(f"📊 Generated articles: {processed_count}")
        print(f"🤖 Model usage:")
        print(f"   📝 Gemini 2.5 Flash: {self.session_stats['gemini_used']} articles")
        print(f"   💎 GPT-4o Premium: {self.session_stats['gpt4o_used']} articles")
        print(f"👥 Journalist assignments: {self.session_stats['journalist_assignments']}")
        print(f"❌ Generation errors: {self.session_stats['generation_errors']}")
        print(f"💎 Premium quota used: {self.daily_premium_count}/{self.daily_premium_limit}")
        
        # Usage percentage
        total_processed = self.session_stats['gemini_used'] + self.session_stats['gpt4o_used']
        if total_processed > 0:
            gpt4o_percentage = (self.session_stats['gpt4o_used'] / total_processed) * 100
            print(f"💎 GPT-4o usage: {gpt4o_percentage:.1f}%")

    def _get_fallback_prompt(self, article: Article, model: str, clean_content: str) -> str:
        """Fallback prompt generation"""
        if model == 'gpt4o':
            return f"""
            Készíts részletes, magas minőségű cikket:

            Eredeti cím: {article.original_title}
            Kategória: {getattr(article, 'category', 'general')}
            Fontosság: {getattr(article, 'importance_score', 8)}/20
            Forrás: {article.source}
            Tartalom: {clean_content}

            KRITIKUS KÖVETELMÉNYEK:
            - MINIMUM 800-1200 szavas részletes cikk MAGYARUL
            - KÖTELEZŐ MAGYAR NYELV - forrás nyelvétől függetlenül
            - Professzionális újságírói stílus
            - Kontextus és háttér információk
            - Minden eredeti tény megtartása
            - Optimalizált magyar cím

            JSON válasz:
            {{
                "article_body": "minimum 800-1200 szavas részletes MAGYAR cikk...",
                "title": "optimalizált magyar cím",
                "sentiment": "positive/negative/neutral",
                "keywords": "magyar kulcsszó1, kulcsszó2, kulcsszó3, kulcsszó4"
            }}
            """
        else:
            return f"""
            Írj informatív cikket:

            Cím: {article.original_title}
            Kategória: {getattr(article, 'category', 'general')}
            Forrás: {article.source}
            Tartalom: {clean_content}

            KRITIKUS KÖVETELMÉNYEK:
            - MINIMUM 600-800 szavas informatív cikk MAGYARUL
            - KÖTELEZŐ MAGYAR NYELV - forrás nyelvétől függetlenül
            - Közérthető magyar újságírói stílus
            - Minden eredeti tény és adat megtartása
            - Lényegi információk + kontextus

            JSON válasz:
            {{
                "article_body": "minimum 600-800 szavas MAGYAR cikk...",
                "title": "optimalizált magyar cím",
                "sentiment": "positive/negative/neutral",
                "keywords": "magyar kulcsszó1, kulcsszó2, kulcsszó3, kulcsszó4"
            }}
            """

    # === BACKWARD COMPATIBILITY METHODS ===
    
    def process_unprocessed_articles(self) -> int:
        """
        Backward compatibility method for v4.1 orchestrator.
        This method now delegates to the editorial_ai + generation workflow.
        """
        print("⚠️ DEPRECATED: process_unprocessed_articles() called")
        print("   → Consider upgrading to v6.0 orchestrator with editorial_ai.py v5.0 integration")
        
        # For now, fall back to basic processing
        db = get_db_session()
        try:
            unprocessed = db.query(Article).filter(
                Article.is_processed == False
            ).limit(20).all()
            
            if not unprocessed:
                return 0
            
            # Set basic attributes if missing
            for article in unprocessed:
                if not hasattr(article, 'importance_score'):
                    article.importance_score = 8
                if not hasattr(article, 'category') or not article.category:
                    article.category = 'general'
            
            return self.process_articles_for_generation(unprocessed)
            
        finally:
            db.close()

# Kompatibilitási aliasok
DualPhaseAIProcessor = StrategicDualPhaseAIProcessor
IntegratedDualPhaseAIProcessor = StrategicDualPhaseAIProcessor

def main():
    """Fő AI feldolgozás - BEFEHLSKETTE v5.0 + FEUERLEITANLAGE"""
    processor = StrategicDualPhaseAIProcessor()
    try:
        # Use backward compatibility method for now
        processed = processor.process_unprocessed_articles()
        print(f"✅ BEFEHLSKETTE v5.0 + FEUERLEITANLAGE content generation complete: {processed} articles")
        return processed
    except Exception as e:
        print(f"❌ BEFEHLSKETTE v5.0 + FEUERLEITANLAGE generation error: {str(e)}")
        print(f"   - Traceback: \n{traceback.format_exc()}")
        return 0

if __name__ == "__main__":
    main()