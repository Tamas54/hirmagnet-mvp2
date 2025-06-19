# ai/prompt_manager.py - CLAUS PRECISION PROMPT MANAGEMENT SYSTEM
# ACHTUNG! Backward compatibility ist KRITISCH!

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
import re

class PromptManager:
    """
    German Engineering Prompt Management System
    MAINTAINS FULL BACKWARD COMPATIBILITY!
    """
    
    def __init__(self):
        self.prompts_dir = Path("ai/prompts")
        self.cache = {}
        self.ensure_prompt_structure()
        
        print("🎯 PromptManager initialized - German precision enabled!")
    
    def ensure_prompt_structure(self):
        """Create prompt directory structure if not exists"""
        directories = [
            "ai/prompts/editorial",
            "ai/prompts/processing", 
            "ai/prompts/journalists/premium_analysts",
            "ai/prompts/journalists/hybrid_experts", 
            "ai/prompts/journalists/gemini_team"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create default prompts if they don't exist
        self.create_default_prompts()
    
    def create_default_prompts(self):
        """Create default prompt files with current system prompts"""
        
        default_prompts = {
            # EDITORIAL PROMPTS
            "editorial/duplicate_detection.txt": """Elemezd ezt a magyar cikket és készíts téma ujjlenyomatot duplikátum detektáláshoz:

Cím: {title}
Forrás: {source}
Tartalom: {content}

FONTOS: Koncentrálj a FŐ TÉMÁRA, ne a részletekre!

JSON válasz:
{{
    "main_topic": "fő téma 2-4 szóban (pl: orbán bejelentés, mészáros üzlet)",
    "key_entities": ["kulcs személyek/helyek/szervezetek max 4"],
    "event_type": "esemény típusa (bejelentés/botrány/döntés/baleset stb)",
    "geographic_scope": "helyszín (budapest/magyarország/nemzetközi)",
    "core_subject": "mi a lényeg egy mondatban"
}}

Példák:
- "Orbán Viktor új törvényt jelentett be" → main_topic: "orbán törvény"
- "Mészáros Lőrinc cége nyert tender" → main_topic: "mészáros tender" 
- "Ukrajna támadás Oroszország" → main_topic: "ukrajna támadás"
""",

            # PROCESSING PROMPTS  
            "processing/categorization_and_scoring.txt": """Elemezd ezt a magyar hírportálos cikket és határozd meg:

CIKK ADATOK:
Cím: {title}
Forrás: {source}
Jelenlegi kategória: {category}
Tartalom: {content}

FELADATOK:
1. Határozd meg a VALÓDI kategóriát a tartalom alapján (nem a forrás alapján!)
2. Adj fontossági pontszámot 1-20 skálán (ÚJ SKÁLA!)
3. Indokold a döntést

KATEGÓRIÁK: politics, economy, tech, sport, entertainment, foreign, lifestyle, health, general

⚠️ FONTOS - 20-PONTOS FONTOSSÁGI SKÁLA (LÉGY SZIGORÚ!):
- 19-20: WORLD BREAKING NEWS (világháború, terrortámadás, természeti katasztrófa)
- 17-18: NEMZETI BREAKING NEWS (kormányválság, miniszterelnök lemondás, nagy katasztrófa)
- 15-16: KRITIKUS FONTOSSÁG (fontos törvények, nagy bűnügyek, EU döntések) 
- 13-14: NAGY FONTOSSÁG (kormány bejelentések, nagy cégek, miniszteri hírek)
- 11-12: FONTOS HÍREK (parlamenti döntések, tőzsdei mozgások, sport eredmények)
- 9-10: KÖZEPES FONTOSSÁG (standard politikai nyilatkozatok, cégügyek, kulturális események)
- 7-8: ALACSONY FONTOSSÁG (rutinpolitika, celebrity hírek, lifestyle)
- 5-6: MINIMÁLIS FONTOSSÁG (triviális bulvár, divat hírek)
- 3-4: NAGYON ALACSONY (receptek, horoszkóp)
- 1-2: IRRELEVÁNS (spam, reklám tartalom)

⚠️ CSAK valódi breaking news és komoly válságok kapjanak 15+ pontot!

VÁLASZOLJ JSON FORMÁTUMBAN:
{{
    "real_category": "kategória",
    "importance_score": 1-20,
    "reasoning": "miért ez a kategória és pontszám"
}}""",

            # GPT-4O CONTENT GENERATION
            "processing/gpt4o_content_generation.txt": """Készíts egy hosszú, részletes, minőségi cikket egy magyar hírportálhoz.

EREDETI ANYAG:
Cím: {title}
Kategória: {category}
Fontosság: {importance_score}/20
Tartalom: {content}

FELADATOK:
1. Írj 800-1200 szavas, részletes cikket magyarul
2. Használd szakmai újságírói stílust
3. Add meg a hátteret, kontextust, következményeket
4. Készíts optimális címet
5. Határozd meg az érzelmi tónust
6. Adj 5-8 SEO kulcsszót

JSON VÁLASZ:
{{
    "summary": "teljes 800-1200 szavas cikk...",
    "title": "optimalizált cím",
    "sentiment": "positive/negative/neutral",
    "keywords": "kulcsszó1, kulcsszó2, kulcsszó3, kulcsszó4, kulcsszó5"
}}""",

            # GEMINI CONTENT GENERATION
            "processing/gemini_content_generation.txt": """Írj egy 800-1200 szavas, részletes cikket magyar hírportálhoz.

ALAPANYAG:
Cím: {title}
Kategória: {category}
Tartalom: {content}

FELADATOK:
1. 800-1200 szavas, részletes informatív cikk
2. Magyar újságírói stílus
3. Lényeges információk + kontextus + háttér
4. Olvasható, optimalizált címet adj
5. Érzelmi tónus meghatározása
6. 5-7 SEO kulcsszó

JSON-ban válaszolj:
{{
    "summary": "800-1200 szavas részletes cikk...",
    "title": "optimalizált cím",
    "sentiment": "positive/negative/neutral",
    "keywords": "kulcsszó1, kulcsszó2, kulcsszó3, kulcsszó4, kulcsszó5"
}}"""
        }
        
        # Write default prompts if they don't exist
        for file_path, content in default_prompts.items():
            full_path = self.prompts_dir / file_path
            if not full_path.exists():
                full_path.write_text(content, encoding='utf-8')
                print(f"✅ Created default prompt: {file_path}")
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Get prompt with variable substitution
        BACKWARD COMPATIBLE!
        """
        try:
            # Handle old-style prompt names for compatibility
            prompt_path = self._resolve_prompt_path(prompt_name)
            
            # Load from cache or file
            if prompt_path not in self.cache:
                full_path = self.prompts_dir / prompt_path
                if full_path.exists():
                    self.cache[prompt_path] = full_path.read_text(encoding='utf-8')
                else:
                    # FALLBACK: Return hardcoded prompt for compatibility
                    return self._get_fallback_prompt(prompt_name, **kwargs)
            
            prompt_template = self.cache[prompt_path]
            
            # Variable substitution
            return self._substitute_variables(prompt_template, **kwargs)
            
        except Exception as e:
            print(f"⚠️ Prompt loading error for {prompt_name}: {e}")
            # CRITICAL: Return fallback to maintain compatibility
            return self._get_fallback_prompt(prompt_name, **kwargs)
    
    def _resolve_prompt_path(self, prompt_name: str) -> str:
        """Resolve prompt name to file path"""
        
        # Map old prompt names to new file paths for compatibility
        name_mapping = {
            "duplicate_detection": "editorial/duplicate_detection.txt",
            "categorization": "processing/categorization_and_scoring.txt", 
            "gpt4o_generation": "processing/gpt4o_content_generation.txt",
            "gemini_generation": "processing/gemini_content_generation.txt"
        }
        
        return name_mapping.get(prompt_name, f"{prompt_name}.txt")
    
    def _substitute_variables(self, template: str, **kwargs) -> str:
        """Substitute variables in template"""
        try:
            # Simple variable substitution using format
            return template.format(**kwargs)
        except KeyError as e:
            print(f"⚠️ Missing variable in prompt: {e}")
            # Return template as-is if substitution fails
            return template
    
    def _get_fallback_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        CRITICAL FALLBACK PROMPTS 
        Ensures backward compatibility if files are missing!
        """
        
        fallbacks = {
            "duplicate_detection": """
            Elemezd ezt a magyar cikket és készíts téma ujjlenyomatot duplikátum detektáláshoz:

            Cím: {title}
            Forrás: {source}
            Tartalom: {content}

            JSON válasz:
            {{
                "main_topic": "fő téma 2-4 szóban",
                "key_entities": ["kulcs személyek/helyek"],
                "event_type": "esemény típusa",
                "geographic_scope": "helyszín",
                "core_subject": "mi a lényeg egy mondatban"
            }}
            """,
            
            "categorization": """
            Elemezd ezt a cikket:
            Cím: {title}
            Tartalom: {content}
            
            JSON válasz:
            {{
                "real_category": "kategória",
                "importance_score": 1-20,
                "reasoning": "indoklás"
            }}
            """
        }
        
        fallback = fallbacks.get(prompt_name, "System prompt unavailable. Contact administrator.")
        
        try:
            return fallback.format(**kwargs)
        except:
            return fallback
    
    def list_available_prompts(self) -> Dict[str, list]:
        """List all available prompts by category"""
        prompts = {
            "editorial": [],
            "processing": [], 
            "journalists": []
        }
        
        for category in prompts.keys():
            category_path = self.prompts_dir / category
            if category_path.exists():
                prompts[category] = [f.name for f in category_path.glob("*.txt")]
        
        return prompts
    
    def reload_prompts(self):
        """Clear cache and reload all prompts"""
        self.cache.clear()
        print("🔄 Prompt cache cleared - prompts will be reloaded")
    
    def update_prompt(self, prompt_name: str, new_content: str):
        """Update a prompt file"""
        try:
            prompt_path = self._resolve_prompt_path(prompt_name)
            full_path = self.prompts_dir / prompt_path
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write new content
            full_path.write_text(new_content, encoding='utf-8')
            
            # Update cache
            self.cache[prompt_path] = new_content
            
            print(f"✅ Updated prompt: {prompt_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update prompt {prompt_name}: {e}")
            return False

# GLOBAL INSTANCE for backward compatibility
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """Get global prompt manager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager

def get_prompt(prompt_name: str, **kwargs) -> str:
    """Convenience function for getting prompts"""
    return get_prompt_manager().get_prompt(prompt_name, **kwargs)

# BACKWARD COMPATIBILITY FUNCTIONS
def load_prompt_from_file(filename: str, **kwargs) -> str:
    """Legacy function for backward compatibility"""
    return get_prompt(filename, **kwargs)

if __name__ == "__main__":
    # Test the prompt manager
    pm = PromptManager()
    print("🧪 Testing prompt manager...")
    
    # Test prompt loading
    test_prompt = pm.get_prompt("categorization", 
                               title="Test cikk", 
                               content="Test tartalom",
                               category="general")
    
    print("✅ Prompt manager test successful!")
    print(f"Available prompts: {pm.list_available_prompts()}")
