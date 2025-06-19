# ai/editorial_ai.py - v5.0 - OPERATION EFFIZIENZ
# Egyesített, intelligens előfeldolgozás

import google.generativeai as genai
from typing import List, Dict, Optional, Any
import time
import re
import json
import os
from difflib import SequenceMatcher

# A rendszer többi részével való kompatibilitás megőrzése
from database.models import Article
try:
    from ai.prompt_manager import get_prompt_manager
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False


class StrategicEditorialAI:
    """
    🧲 HírMagnet Strategic Editorial AI v5.0 - EFFIZIENZ
    
    NEUE FEATURES in v5.0:
    ✅ Egyesített Felderítési Protokoll: Kategorizálás, fontosság-becslés és duplikátum-ujjlenyomat egyetlen AI hívással.
    ✅ A "buta" kulcsszavas szűrő teljes kiiktatása.
    ✅ Drámaian csökkentett hibaszázalék és megnövelt hatékonyság.
    ✅ Gemini 2.5 Flash az intelligens elemzéshez.
    ✅ Finomhangolt 0.55 similarity threshold az optimális duplikátum-detektáláshoz.
    """
    
    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
            print("✅ Strategic Editorial AI v5.0 (EFFIZIENZ) inicializálva Gemini 2.5 Flash-sel")
        else:
            self.gemini_model = None
            print("⚠️ GEMINI_API_KEY hiányzik! Editorial AI letiltva.")
        
        # A PromptManager itt már csak fallback célokat szolgálhat, a fő prompt belső.
        self.prompt_manager = get_prompt_manager() if PROMPT_MANAGER_AVAILABLE else None

    def _get_unified_analysis_prompt(self, article: Article) -> str:
        """
        Létrehozza az új, EGYESÍTETT FELDERÍTÉSI ÉS BESOROLÁSI PARANCS v1.1-et.
        """
        clean_content = self._clean_content(article.original_content or "")
        return f"""
        Elemezd a következő magyar hírcikket a megadott szempontok szerint. A válaszodat kizárólag egyetlen, valid JSON objektumként add vissza.

        CIKK CÍME: {article.original_title}
        CIKK TARTALMA (RÉSZLET): {clean_content[:2500]}

        FELADATOK:
        1.  **Kategorizálás:** Határozd meg a cikk legpontosabb kategóriáját a következő, zárt listából: [politics, economy, tech, sport, entertainment, foreign, lifestyle, cars, general]. A döntésed a cikk valós tartalmán alapuljon.
        2.  **Fontosság Becslése:** Adj egy előzetes fontossági pontszámot 1-20 közötti skálán, ahol a 20 a világszinten is kiemelt hír.
        3.  **Duplikátum Ujjlenyomat:** Hozz létre egy téma-ujjlenyomatot a cikkről a későbbi duplikátum-szűréshez.
            - **KRITIKUS PARANCS:** Az ujjlenyomatot a CÍM **ÉS** a TARTALOM együttes elemzése alapján kell létrehozni a maximális pontosság érdekében!
            - `main_topic`: A cikk fő témája 2-4 szóban (pl. "kormányinfó bejelentés", "új iPhone modell").
            - `key_entities`: A cikkben szereplő legfontosabb személyek, helyek, szervezetek (maximum 4).

        VÁLASZ KIZÁRÓLAG JSON FORMÁTUMBAN:
        {{
            "real_category": "meghatározott_kategória",
            "importance_score": "<1-20 közötti egész szám>",
            "duplicate_fingerprint": {{
                "main_topic": "fő téma 2-4 szóban",
                "key_entities": ["entitás_1", "entitás_2"]
            }},
            "reasoning": "Rövid, 1-2 mondatos indoklás a kategória és fontosság választásáról."
        }}
        """

    def _get_unified_analysis(self, article: Article) -> Optional[Dict]:
        """Egyetlen AI hívással lefuttatja a kategorizálást, fontosság-becslést és ujjlenyomat-készítést."""
        if not self.gemini_model:
            return None
        
        prompt = self._get_unified_analysis_prompt(article)
        try:
            response = self.gemini_model.generate_content(prompt)
            json_text_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_text_match:
                return json.loads(json_text_match.group(0))
            print(f"      ⚠️ AI Unified Analysis - JSON nem található a válaszban: {response.text}")
            return None
        except Exception as e:
            print(f"      ⚠️ AI Unified Analysis hiba: {str(e)}")
            return None

    def process_articles_editorial(self, articles: List[Article]) -> Dict[str, Any]:
        """A teljes, új, intelligens előfeldolgozási csővezeték."""
        if not self.gemini_model:
            return {"kept": articles, "duplicates": [], "merged": [], "analysis": {}}

        print(f"\n📝 STRATEGIC EDITORIAL AI v5.0 PROCESSING (EFFIZIENZ PROTOKOLL)")
        print(f"📊 Input: {len(articles)} cikk")
        
        # 1. FÁZIS: EGYESÍTETT AI ELEMZÉS MINDEN CIKKRE
        print("🤖 Phase 1: Egyesített AI elemzés futtatása...")
        start_time = time.time()
        
        for article in articles:
            analysis = self._get_unified_analysis(article)
            # Az eredményt ideiglenesen az objektumhoz csatoljuk
            article.ai_analysis = analysis if analysis else {
                "real_category": article.category, "importance_score": 8,
                "duplicate_fingerprint": {"main_topic": article.original_title[:30], "key_entities": []},
                "reasoning": "AI analysis fallback"
            }
            # A kategóriát és a pontszámot azonnal frissítjük az objektumon
            article.category = article.ai_analysis.get("real_category", article.category)
            article.importance_score = article.ai_analysis.get("importance_score", 8)
            
            print(f"   📊 {article.source}: {article.category} (score: {article.importance_score})")
            time.sleep(0.3) # Rate limiting

        print(f"   ✅ Elemzés kész: {time.time() - start_time:.1f}s")

        # 2. FÁZIS: DUPLIKÁTUM-SZŰRÉS AZ AI UJJLENYOMATOK ALAPJÁN
        print("🔍 Phase 2: Duplikátum-szűrés az intelligens ujjlenyomatok alapján...")
        kept_articles: List[Article] = []
        duplicates: List[Article] = []
        # A 'processed_topics' mostantól a már megtartott cikkek listája lesz
        
        # Először rendezzük a cikkeket a kapott fontosság szerint, hogy a fontosabb maradjon meg
        sorted_articles = sorted(articles, key=lambda a: a.importance_score, reverse=True)

        for article in sorted_articles:
            is_duplicate = False
            current_fingerprint = article.ai_analysis.get("duplicate_fingerprint", {})
            
            for kept_article in kept_articles:
                # Hasonlósági pontszám számítása a két ujjlenyomat között
                kept_fingerprint = kept_article.ai_analysis.get("duplicate_fingerprint", {})
                similarity = self._calculate_fingerprint_similarity(current_fingerprint, kept_fingerprint)
                
                # FINOMHANGOLT THRESHOLD: 0.55 (volt: 0.75)
                if similarity > 0.55:
                    is_duplicate = True
                    print(f"   🗑️ Duplikátum (sim: {similarity:.2f}): [{article.source}] '{article.original_title[:40]}...' ~ [{kept_article.source}] '{kept_article.original_title[:40]}...'. Elvetve.")
                    duplicates.append(article)
                    break

            if not is_duplicate:
                kept_articles.append(article)
                print(f"   ✅ Megtartva: [{article.source}] '{article.original_title[:40]}...' (score: {article.importance_score})")
        
        print(f"\n   📊 Szűrés kész:")
        print(f"      ✅ Megtartva: {len(kept_articles)} cikk")
        print(f"      🗑️ Duplikátumok: {len(duplicates)} cikk")
        print(f"      📈 Duplikátum arány: {(len(duplicates)/len(articles)*100):.1f}%")
        
        return {
            "kept": kept_articles,
            "duplicates": duplicates,
            "merged": [],
            "analysis": {
                "message": "Efficiency Protocol Complete", 
                "duplicate_rate": len(duplicates)/len(articles) if articles else 0,
                "processing_time": time.time() - start_time
            }
        }

    def _calculate_fingerprint_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Kiszámolja a hasonlóságot két AI által generált ujjlenyomat között."""
        if not fp1 or not fp2: 
            return 0.0

        topic1 = fp1.get("main_topic", "").lower()
        topic2 = fp2.get("main_topic", "").lower()
        topic_sim = SequenceMatcher(None, topic1, topic2).ratio()

        entities1 = set([e.lower() for e in fp1.get("key_entities", [])])
        entities2 = set([e.lower() for e in fp2.get("key_entities", [])])
        
        if not entities1 and not entities2: 
            entity_overlap = 0.0
        elif not entities1 or not entities2: 
            entity_overlap = 0.0
        else:
            intersection = len(entities1.intersection(entities2))
            union = len(entities1.union(entities2))
            entity_overlap = intersection / union if union > 0 else 0

        # Weighted combination: 60% topic + 40% entities
        final_similarity = (topic_sim * 0.6) + (entity_overlap * 0.4)
        
        return final_similarity

    def _clean_content(self, content: str) -> str:
        """HTML címkék eltávolítása és egyszerűsítés."""
        if not content: 
            return ""
        # HTML tags removal + whitespace cleanup
        clean = re.sub(r'<[^>]+>', '', content)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def get_session_statistics(self) -> Dict:
        """Enhanced session statistics for v5.0"""
        return {
            "version": "5.0_EFFIZIENZ",
            "gemini_model": "2.5-flash-preview",
            "similarity_threshold": 0.55,
            "features": [
                "unified_analysis", 
                "intelligent_categorization", 
                "ai_fingerprint_deduplication",
                "importance_scoring"
            ],
            "gemini_available": self.gemini_model is not None,
            "prompt_manager_available": self.prompt_manager is not None
        }

# Wrapper class a visszamenőleges kompatibilitásért
class EnhancedEditorialAI(StrategicEditorialAI):
    """
    EnhancedEditorialAI - Wrapper a StrategicEditorialAI-hoz
    Átirányítja a funkcionalitást a StrategicEditorialAI-ra.
    """
    def __init__(self):
        super().__init__()
        print("✅ EnhancedEditorialAI inicializálva (StrategicEditorialAI v5.0 wrapper)")
    
    def process_articles_editorial(self, articles: List[Article]) -> Dict:
        """
        Átirányítja a feldolgozást a StrategicEditorialAI-ra
        """
        return super().process_articles_editorial(articles)

def main():
    """Strategic Editorial AI v5.0 testing"""
    print("🧪 Strategic Editorial AI v5.0 EFFIZIENZ teszt...")
    
    editorial = StrategicEditorialAI()
    
    # Basic functionality test
    stats = editorial.get_session_statistics()
    print(f"✅ Version: {stats['version']}")
    print(f"✅ Gemini Model: {stats['gemini_model']}")
    print(f"✅ Similarity Threshold: {stats['similarity_threshold']}")
    print(f"✅ Features: {', '.join(stats['features'])}")
    
    print("🎯 Strategic Editorial AI v5.0 EFFIZIENZ ready for deployment!")

if __name__ == "__main__":
    main()
