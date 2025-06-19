# ai/v5_orchestrator.py - v5.3 - OPERATION EINHEIT ULTIMATE
# A végső, letisztult architektúra + enhanced error logging + dotenv

# .env fájl betöltése ELSŐ lépésként
from dotenv import load_dotenv
load_dotenv()

import asyncio
import time
import json
import traceback  # Enhanced error logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import os
import sys

# === DATABASE & SQL IMPORTS ===
from sqlalchemy import case, func
from sqlalchemy.sql.expression import literal_column

# KRITISCHE PATH KORREKTUR!
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Database imports
from database.db import get_db_session
from database.models import Article, ProcessingLog

# A hadtest végrehajtó egységeinek importálása
from ai.processor import StrategicDualPhaseAIProcessor
from ai.editorial_ai import StrategicEditorialAI
try:
    from ai.journalists import get_journalist_manager
    JOURNALIST_MANAGER_AVAILABLE = True
except ImportError:
    JOURNALIST_MANAGER_AVAILABLE = False

class ChimeraDualChannelOrchestrator:
    """
    🎖️ OPERATION CHIMERA v5.3 - EINHEIT ULTIMATE
    
    NEUE ARCHITEKTUR + ENHANCED DIAGNOSTICS:
    ✅ Tiszta parancsnoki lánc: Editorial AI → Orchestrator → Processor
    ✅ Zero redundancy: Minden felelősség egyszer, egy helyen
    ✅ Moduláris design: Komponensek független fejleszthetősége
    ✅ Backward compatibility: Meglévő interfészek támogatása
    ✅ Fresh article identification: Intelligens frissesség-alapú szűrés
    ✅ Performance optimization: Párhuzamos feldolgozás
    ✅ Enhanced error logging: Részletes hibakezelés
    ✅ Dotenv support: Környezeti változók automatikus betöltése
    
    Tiszta parancsnoki lánc: Az EditorialAI dönt, a Chimera végrehajt.
    """
    
    def __init__(self):
        print("🎖️ INITIALIZING OPERATION CHIMERA v5.3 (EINHEIT ULTIMATE)...")
        print("🏗️ Clean Architecture: Editorial AI → Orchestrator → Processor")
        print("🔧 Enhanced Diagnostics: dotenv + error logging enabled")
        
        # A Kiméra mostantól csak a végrehajtó egységeket koordinálja
        self.processor = StrategicDualPhaseAIProcessor()
        self.editorial_ai = StrategicEditorialAI()
        
        if JOURNALIST_MANAGER_AVAILABLE:
            self.journalist_manager = get_journalist_manager()
            print("👥 Journalist corps: READY!")
        else:
            self.journalist_manager = None
            print("⚠️ Journalist corps: UNAVAILABLE")
        
        # A csatorna-definíciók megmaradnak a routinghoz
        self.blitz_channels = {"lifestyle", "entertainment", "cars", "sport"}
        
        # Fresh article limits (kept from v5.2)
        self.fresh_article_limits = {
            "first_run": 200,
            "hourly_update": 100,
            "maintenance": 50
        }
        
        # Performance tracking
        self.performance_metrics = {
            "fresh_articles_identified": 0,
            "editorial_processed": 0,
            "duplicates_removed": 0,
            "blitz_processed": 0,
            "strategic_processed": 0,
            "generation_errors": 0,
            "total_time": 0
        }
        
        print("🎯 CHIMERA v5.3 ORCHESTRATOR: CLEAN ARCHITECTURE + DIAGNOSTICS - OPERATIONAL!")
    
    def identify_fresh_articles(self, cutoff_hours: int = 2, max_articles: int = 50, mode: str = "hourly_update") -> Tuple[List[Article], int]:
        """
        🔍 FRESH ARTICLE IDENTIFICATION (kept from v5.2)
        Intelligens frissesség-alapú szűrés source priority-vel
        """
        db = get_db_session()
        try:
            if mode == "first_run":
                max_articles = self.fresh_article_limits["first_run"]
                cutoff_hours = 24
            elif mode == "hourly_update":
                max_articles = self.fresh_article_limits["hourly_update"]
                cutoff_hours = 2
            elif mode == "maintenance":
                max_articles = self.fresh_article_limits["maintenance"]
                cutoff_hours = 1
            
            now = datetime.now()
            cutoff_time = now - timedelta(hours=cutoff_hours)
            
            # === SMART SOURCE PRIORITY MATRIX ===
            fpp_case = case(
                (
                    Article.source.in_([
                        'The Intercept', 'ProPublica', 'Bellingcat', 'OCCRP', 
                        'The Economist - Finance', 'The Economist - Business', 'Bloomberg Markets'
                    ]), 120  # Elite Tier 1
                ),
                (
                    Article.source.in_([
                        'BBC News UK', 'BBC News World', 'CNN Latest', 'The Guardian World'
                    ]), 110 # Elite Tier 2
                ),
                (
                     Article.source.in_([
                        'TechCrunch', 'The Verge', 'WIRED Business', 'Ars Technica'
                     ]), 100 # Elite Tier 3
                ),
                (
                    Article.source.in_([
                        'Portfolio', 'G7', 'HVG', 'Telex', 'Válasz Online', 'Qubit'
                    ]), 80 # Premium Domestic
                ),
                (
                    Article.source.in_([
                        'Index', '24.hu', '444.hu', 'Magyar Nemzet'
                    ]), 60 # Standard Domestic
                ),
                else_=30 # Others
            ).label("fpp")

            # === FRESHNESS BONUS ===
            fbp_case = case(
                (Article.published_at >= now - timedelta(minutes=30), 120), # Breaking news
                (Article.published_at >= now - timedelta(hours=2), 50),     # Fresh
                else_=0
            ).label("fbp")

            # === GLOBAL TACTICAL PRIORITY (GTP) ===
            gtp_score = (literal_column("fpp") + literal_column("fbp")).label("gtp")
            
            fresh_articles_query = db.query(
                Article,
                gtp_score
            ).select_from(Article).add_columns(fpp_case, fbp_case).filter(
                Article.is_processed == False,
                Article.published_at >= cutoff_time
            ).order_by(
                gtp_score.desc()
            ).limit(max_articles)

            fresh_articles = [article for article, score in fresh_articles_query.all()]
            
            old_unprocessed = db.query(Article).filter(
                Article.is_processed == False,
                Article.published_at < cutoff_time
            ).count()
            
            self.performance_metrics["fresh_articles_identified"] = len(fresh_articles)
            
            print(f"🔍 Fresh articles identified: {len(fresh_articles)}/{max_articles} (cutoff: {cutoff_hours}h)")
            print(f"🛡️ Old articles ignored: {old_unprocessed}")
            
            if fresh_articles:
                top_article = fresh_articles[0]
                print(f"🥇 Top priority: {top_article.source} - {top_article.original_title[:40]}...")
            
            return fresh_articles, old_unprocessed
            
        finally:
            db.close()
    
    def categorize_articles_by_channel(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """
        🎯 CLEAN CHANNEL ROUTING
        A metódus mostantól nem végez saját kategorizálást. A döntést
        az `editorial_ai` által már beállított kategória és pontszám alapján hozza meg.
        """
        channels = {"blitz": [], "strategic": []}
        
        for article in articles:
            # A döntés az ELŐZŐLEG MEGHATÁROZOTT ADATOKON ALAPUL
            category = getattr(article, 'category', 'general')
            importance = getattr(article, 'importance_score', 8)
            
            # Clean routing logic
            is_strategic = (
                category in ["politics", "foreign", "economy"] or  # Core strategic categories
                importance >= 14 or  # High importance threshold
                (category == "tech" and importance >= 12)  # Tech with medium+ importance
            )
            
            if is_strategic:
                channels["strategic"].append(article)
            else:
                channels["blitz"].append(article)
        
        print(f"🚄 Blitz Channel: {len(channels['blitz'])} article(s)")
        print(f"🎯 Strategic Channel: {len(channels['strategic'])} article(s)")
        
        return channels
    
    async def process_blitz_channel(self, articles: List[Article]) -> Dict[str, Any]:
        """🚄 BLITZ CHANNEL - Fast, efficient processing for lighter content"""
        if not articles:
            return {"processed": 0, "time": 0}
        
        print(f"🚄 BLITZ CHANNEL START: {len(articles)} articles processing...")
        start_time = time.time()
        
        try:
            # Enhanced logging for blitz articles
            for article in articles:
                print(f"   🚄 Blitz article: {article.original_title[:40]}... (score: {getattr(article, 'importance_score', 0)})")
            
            # Process all articles in batch
            processed_count = self.processor.process_articles_for_generation(articles)
            
            processing_time = time.time() - start_time
            print(f"🚄 BLITZ CHANNEL COMPLETE: {processed_count} articles in {processing_time:.1f}s")
            
            self.performance_metrics["blitz_processed"] = processed_count
            
            return {
                "processed": processed_count,
                "time": processing_time,
                "efficiency": processed_count / max(1, processing_time)
            }
            
        except Exception as e:
            print(f"❌ BLITZ CHANNEL ERROR: {type(e).__name__}: {str(e)}")
            print(f"   Traceback: \n{traceback.format_exc()}")
            self.performance_metrics["generation_errors"] += 1
            return {"processed": 0, "time": time.time() - start_time, "error": str(e)}

    async def process_strategic_channel(self, articles: List[Article]) -> Dict[str, Any]:
        """🎯 STRATEGIC CHANNEL - Premium deep analysis with enhanced error handling"""
        if not articles:
            return {"processed": 0, "time": 0, "results": []}

        print(f"🎯 STRATEGIC CHANNEL START: {len(articles)} articles processing...")
        start_time = time.time()
        
        processed_count = 0
        successful_articles = []
        
        try:
            for i, article in enumerate(articles):
                try:
                    print(f"\n   🎯 Processing {i+1}/{len(articles)}: {article.original_title[:50]}...")
                    print(f"      📊 Category: {getattr(article, 'category', 'general')}, Importance: {getattr(article, 'importance_score', 0)}/20")
                    
                    # Újságíró kijelölés enhanced logging-gal
                    journalist_assignment = None
                    if self.journalist_manager:
                        journalist_assignment = self.journalist_manager.select_journalist_for_article(
                            getattr(article, 'category', 'general'),
                            getattr(article, 'importance_score', 8),
                            getattr(article, 'original_content', '') or ''
                        )
                        
                        if journalist_assignment:
                            print(f"      👤 Journalist: {journalist_assignment['journalist_name']}")
                            print(f"         📊 Expertise: {', '.join(journalist_assignment.get('expertise', []))}")
                            print(f"         🎯 Score: {journalist_assignment.get('score', 0):.2f}")
                    
                    # Model selection
                    model_to_use = self.processor._determine_model(
                        getattr(article, 'importance_score', 8), 
                        journalist_assignment
                    )
                    print(f"      🤖 Model: {model_to_use.upper()}")
                    
                    # Content generation with enhanced error handling
                    content_result = self.processor._generate_final_content(article, model_to_use, journalist_assignment)
                    
                    if content_result and content_result.get('article_body'):
                        # Successful generation - update database
                        db = get_db_session()
                        try:
                            article.ai_summary = content_result.get('article_body')
                            article.ai_title = content_result.get('title')
                            article.sentiment = content_result.get('sentiment')
                            article.seo_keywords = content_result.get('keywords')
                            article.is_processed = True
                            article.processing_model = f"strategic_{model_to_use}"
                            
                            if journalist_assignment:
                                article.assigned_journalist = journalist_assignment.get('journalist_id')
                                article.journalist_name = journalist_assignment.get('journalist_name')
                            
                            db.merge(article)
                            db.commit()
                            processed_count += 1
                            successful_articles.append(article)
                            
                            print(f"      ✅ Content generated successfully (ID: {article.id})")
                            
                        except Exception as db_error:
                            print(f"      ❌ Database error for article {article.id}: {type(db_error).__name__}: {str(db_error)}")
                            db.rollback()
                            self.performance_metrics["generation_errors"] += 1
                        finally:
                            db.close()
                    else:
                        print(f"      ⚠️ Content generation failed - no valid content returned")
                        self.performance_metrics["generation_errors"] += 1
                
                except Exception as article_error:
                    print(f"      ❌ Article processing error (ID: {getattr(article, 'id', 'unknown')}): {type(article_error).__name__}: {str(article_error)}")
                    print(f"         Traceback: \n{traceback.format_exc()}")
                    self.performance_metrics["generation_errors"] += 1
                    continue
                    
                # Rate limiting
                await asyncio.sleep(0.3)
        
        except Exception as channel_error:
            print(f"❌ STRATEGIC CHANNEL CRITICAL ERROR: {type(channel_error).__name__}: {str(channel_error)}")
            print(f"   Traceback: \n{traceback.format_exc()}")
        
        processing_time = time.time() - start_time
        print(f"\n🎯 STRATEGIC CHANNEL COMPLETE: {processed_count}/{len(articles)} articles in {processing_time:.1f}s")
        
        if self.performance_metrics["generation_errors"] > 0:
            print(f"⚠️ Generation errors encountered: {self.performance_metrics['generation_errors']}")
        
        self.performance_metrics["strategic_processed"] = processed_count
        
        return {
            "processed": processed_count,
            "time": processing_time,
            "articles_analyzed": len(articles),
            "successful_articles": successful_articles,
            "errors": self.performance_metrics["generation_errors"]
        }
    
    async def run_full_process(self, articles: List[Article] = None, mode: str = "hourly_update") -> Dict[str, Any]:
        """
        🎖️ MAIN UNIFIED PIPELINE v5.3 ULTIMATE
        A teljes, letisztült feldolgozási lánc enhanced error handling-gal:
        1. Fresh article identification (ha nincs input)
        2. Editorial AI előfeldolgozás (kategorizálás + duplikátum-szűrés)
        3. Channel routing
        4. Parallel content generation with enhanced diagnostics
        """
        print("\n" + "="*60)
        print(f"🎖️ OPERATION CHIMERA v5.3 EINHEIT ULTIMATE - MODE: {mode.upper()}")
        print("🏗️ Clean Architecture Pipeline + Enhanced Diagnostics Starting...")
        print("="*60)
        
        total_start_time = time.time()
        
        try:
            # === PHASE 1: FRESH ARTICLE IDENTIFICATION ===
            if articles is None:
                print("🔍 Phase 1: Fresh article identification...")
                articles, old_articles = self.identify_fresh_articles(mode=mode)
                
                if not articles:
                    print("✅ No fresh articles to process. Mission paused.")
                    return {"status": "no_work", "old_articles": old_articles}
            else:
                print(f"🔍 Phase 1: Using provided articles ({len(articles)} items)")
            
            # === PHASE 2: EDITORIAL AI PREPROCESSING ===
            print("📝 Phase 2: Editorial AI preprocessing...")
            editorial_start = time.time()
            
            editorial_results = self.editorial_ai.process_articles_editorial(articles)
            articles_to_process = editorial_results.get("kept", [])
            duplicates_removed = editorial_results.get("duplicates", [])
            
            editorial_time = time.time() - editorial_start
            
            print(f"   ✅ Editorial processing complete: {editorial_time:.1f}s")
            print(f"   📊 Kept: {len(articles_to_process)} articles")
            print(f"   🗑️ Duplicates removed: {len(duplicates_removed)} articles")
            
            self.performance_metrics["editorial_processed"] = len(articles)
            self.performance_metrics["duplicates_removed"] = len(duplicates_removed)

            if not articles_to_process:
                print("✅ Editorial AI filtered out all articles, no further processing needed.")
                return {
                    "status": "editorial_filtered_all",
                    "duplicates_removed": len(duplicates_removed),
                    "editorial_results": editorial_results
                }
            
            # === PHASE 3: CHANNEL ROUTING ===
            print("🎯 Phase 3: Channel routing...")
            channels = self.categorize_articles_by_channel(articles_to_process)
            
            # === PHASE 4: PARALLEL CONTENT GENERATION ===
            print("🚀 Phase 4: Dual channel parallel processing...")
            
            blitz_task = self.process_blitz_channel(channels.get("blitz", []))
            strategic_task = self.process_strategic_channel(channels.get("strategic", []))
            
            blitz_result, strategic_result = await asyncio.gather(
                blitz_task, strategic_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(blitz_result, Exception):
                print(f"❌ Blitz channel critical error: {blitz_result}")
                print(f"   Traceback: \n{traceback.format_exc()}")
                blitz_result = {"processed": 0, "time": 0, "error": str(blitz_result)}
            
            if isinstance(strategic_result, Exception):
                print(f"❌ Strategic channel critical error: {strategic_result}")
                print(f"   Traceback: \n{traceback.format_exc()}")
                strategic_result = {"processed": 0, "time": 0, "error": str(strategic_result)}
            
            # === FINAL METRICS ===
            total_time = time.time() - total_start_time
            total_processed = blitz_result.get("processed", 0) + strategic_result.get("processed", 0)
            
            self.performance_metrics.update({
                "total_time": total_time,
                "total_processed": total_processed
            })
            
            await self._log_results(total_processed, len(articles), editorial_results, blitz_result, strategic_result)
            
            return {
                "status": "success",
                "total_processed": total_processed,
                "input_articles": len(articles),
                "editorial_results": editorial_results,
                "blitz_result": blitz_result,
                "strategic_result": strategic_result,
                "performance_metrics": self.performance_metrics
            }
            
        except Exception as e:
            print(f"❌ CHIMERA v5.3 ULTIMATE ORCHESTRATION ERROR: {type(e).__name__}: {str(e)}")
            print(f"   Traceback: \n{traceback.format_exc()}")
            return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
    
    async def _log_results(self, total_processed: int, input_count: int, editorial_results: Dict, 
                          blitz_result: Dict, strategic_result: Dict):
        """📊 Enhanced logging and reporting"""
        
        print("\n" + "="*60)
        print("📊 OPERATION CHIMERA v5.3 EINHEIT ULTIMATE - MISSION REPORT")
        print("="*60)
        
        print(f"⏱️ Total mission time: {self.performance_metrics['total_time']:.1f}s")
        print(f"📊 Pipeline flow:")
        print(f"   📥 Input articles: {input_count}")
        print(f"   📝 Editorial processed: {self.performance_metrics['editorial_processed']}")
        print(f"   🗑️ Duplicates removed: {self.performance_metrics['duplicates_removed']}")
        print(f"   🚄 Blitz processed: {blitz_result.get('processed', 0)}")
        print(f"   🎯 Strategic processed: {strategic_result.get('processed', 0)}")
        print(f"   ✅ Total content generated: {total_processed}")
        print(f"   ❌ Generation errors: {self.performance_metrics['generation_errors']}")
        
        # Calculate efficiency
        if input_count > 0:
            success_rate = (total_processed / input_count) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Channel performance
        blitz_time = blitz_result.get('time', 0)
        strategic_time = strategic_result.get('time', 0)
        
        if blitz_time > 0:
            blitz_efficiency = blitz_result.get('processed', 0) / blitz_time
            print(f"🚄 Blitz efficiency: {blitz_efficiency:.1f} articles/sec")
        
        if strategic_time > 0:
            strategic_efficiency = strategic_result.get('processed', 0) / strategic_time
            print(f"🎯 Strategic efficiency: {strategic_efficiency:.1f} articles/sec")
        
        print("\n🎯 v5.3 EINHEIT ULTIMATE FEATURES:")
        print("   🏗️ Clean Architecture: ✅")
        print("   📝 Editorial AI Integration: ✅")
        print("   ⚡ Parallel Processing: ✅")
        print("   🔄 Zero Redundancy: ✅")
        print("   🎯 Intelligent Routing: ✅")
        print("   🔧 Enhanced Diagnostics: ✅")
        print("   🌐 Dotenv Support: ✅")
        
        print("\n🎖️ OPERATION CHIMERA v5.3 EINHEIT ULTIMATE: MISSION ACCOMPLISHED!")
        
        # Database logging
        try:
            db = get_db_session()
            log_details = {
                **self.performance_metrics,
                "mode": "chimera_v5.3_einheit_ultimate",
                "editorial_stats": editorial_results.get("session_stats", {}),
                "blitz_stats": blitz_result,
                "strategic_stats": strategic_result
            }
            db.add(ProcessingLog(
                action="chimera_v5.3_einheit_ultimate_orchestration",
                articles_processed=total_processed,
                success=True,
                processing_time=self.performance_metrics['total_time'],
                error_message=json.dumps(log_details)
            ))
            db.commit()
            db.close()
        except Exception as e:
            print(f"⚠️ Logging error: {str(e)}")
    
    # === BACKWARD COMPATIBILITY METHODS ===
    
    async def run_chimera_orchestration(self, mode: str = "hourly_update") -> Dict[str, Any]:
        """🔄 Backward compatibility with v5.2 interface"""
        print("⚠️ DEPRECATED: run_chimera_orchestration() - use run_full_process() instead")
        return await self.run_full_process(mode=mode)
    
    def process_unprocessed_articles(self) -> int:
        """🔄 Backward compatibility with legacy interface"""
        print("⚠️ DEPRECATED: process_unprocessed_articles() - use run_full_process() instead")
        
        # Run the new pipeline synchronously
        result = asyncio.run(self.run_full_process())
        
        if result.get("status") == "success":
            return result.get("total_processed", 0)
        return 0

# === MAIN ENTRY POINTS ===

async def main_orchestration(mode="hourly_update"):
    """Main async entry point"""
    orchestrator = ChimeraDualChannelOrchestrator()
    try:
        return await orchestrator.run_full_process(mode=mode)
    except Exception as e:
        return {"status": "critical_error", "error": str(e)}

def run_chimera_sync(mode="hourly_update"):
    """Synchronous wrapper for async orchestration"""
    return asyncio.run(main_orchestration(mode=mode))

def process_unprocessed_articles():
    """Legacy entry point for backward compatibility"""
    result = run_chimera_sync()
    if result.get("status") == "success":
        return result.get("total_processed", 0)
    return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Chimera v5.3 Orchestrator Ultimate.")
    parser.add_argument('--mode', type=str, default='hourly_update', 
                       help='Run mode: first_run, hourly_update, maintenance')
    args = parser.parse_args()
    
    print(f"🧪 TESTING OPERATION CHIMERA v5.3 EINHEIT ULTIMATE in '{args.mode}' MODE...")
    result = run_chimera_sync(mode=args.mode)
    print(f"\n✅ Test result: {json.dumps(result, indent=2, default=str)}")