"""
AttentionX - Persona Adapter Service
Rewrites content (captions, hooks, tone) for different audiences
"""

import json
from typing import List
from config import GEMINI_API_KEY, PERSONA_CONFIGS


class PersonaAdapter:
    """
    Adapts video content for different audience personas:
    - Students: casual, relatable, learning-focused
    - Entrepreneurs: action-oriented, ROI-focused
    - Developers: technical, pragmatic, precise
    - Marketers: data-driven, growth-focused
    - General: accessible, universal
    """

    def __init__(self):
        self.configs = PERSONA_CONFIGS

    async def adapt(
        self,
        text: str,
        persona: str,
    ) -> dict:
        """
        Adapt content for a specific audience persona.
        
        Returns dict with adapted text, caption, hooks, and tone description.
        """
        config = self.configs.get(persona, self.configs["general"])
        
        # Try AI adaptation first
        ai_result = await self._adapt_with_ai(text, persona, config)
        if ai_result:
            return ai_result
        
        # Fallback to rule-based adaptation
        return self._adapt_rule_based(text, persona, config)

    async def _adapt_with_ai(self, text: str, persona: str, config: dict) -> dict:
        """Adapt content using Gemini AI."""
        if not GEMINI_API_KEY:
            return None
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""You are a content strategist adapting video content for a specific audience.

ORIGINAL CONTENT:
"{text}"

TARGET AUDIENCE: {persona}
TONE: {config['tone']}
VOCABULARY STYLE: {config['vocabulary']}
FOCUS AREAS: {config['focus']}

TASKS:
1. Rewrite the content for this audience (keep the core message, change the delivery)
2. Write a social media caption (2-3 sentences, engaging)
3. Generate 3 viral hooks tailored to this audience
4. Describe the tone shift applied

Return as JSON with these exact keys:
{{
    "adapted_text": "rewritten content",
    "adapted_caption": "social media caption",
    "adapted_hooks": ["hook1", "hook2", "hook3"],
    "tone_description": "description of tone change"
}}

Return ONLY valid JSON, no markdown formatting."""

            response = model.generate_content(prompt)
            
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0]
            
            data = json.loads(response_text)
            
            return {
                "original_text": text,
                "adapted_text": data.get("adapted_text", text),
                "adapted_caption": data.get("adapted_caption", ""),
                "adapted_hooks": data.get("adapted_hooks", []),
                "persona": persona,
                "tone_description": data.get("tone_description", config["tone"]),
            }
            
        except Exception as e:
            print(f"AI persona adaptation error: {e}")
            return None

    def _adapt_rule_based(self, text: str, persona: str, config: dict) -> dict:
        """Rule-based content adaptation fallback."""
        tone = config["tone"]
        
        # Simple tone adaptations
        adapted = text
        caption = ""
        hooks = []
        
        if persona == "students":
            caption = f"📚 Learning moment alert! {text[:100]}... Drop a 🔥 if this hits different!"
            hooks = [
                f"Your professor won't tell you this...",
                f"POV: You finally understand {self._extract_topic(text)}",
                f"Save this for exam season 📌",
            ]
            adapted = f"Okay so check this out — {text}"
            
        elif persona == "entrepreneurs":
            caption = f"💼 Key insight for scaling: {text[:100]}... Save this for your next strategy session."
            hooks = [
                f"This is why most businesses fail at {self._extract_topic(text)}",
                f"Revenue unlock: the {self._extract_topic(text)} framework",
                f"If you're not doing this, you're leaving money on the table",
            ]
            adapted = f"Here's the thing about {self._extract_topic(text)} — {text}"
            
        elif persona == "developers":
            caption = f"🛠️ Dev tip: {text[:100]}... Bookmark this for your next project."
            hooks = [
                f"The {self._extract_topic(text)} pattern nobody uses (but should)",
                f"Code review: Why this {self._extract_topic(text)} approach is superior",
                f"Stop overcomplicating {self._extract_topic(text)}. Here's a better way.",
            ]
            adapted = f"Let's talk about {self._extract_topic(text)}. {text}"
            
        elif persona == "marketers":
            caption = f"📊 Marketing gold: {text[:100]}... This could 10x your engagement."
            hooks = [
                f"The {self._extract_topic(text)} strategy behind viral campaigns",
                f"Data says: {self._extract_topic(text)} drives 3x more engagement",
                f"Stop guessing. Here's what works for {self._extract_topic(text)}.",
            ]
            adapted = f"From a growth perspective, {text}"
            
        else:
            caption = f"✨ Must-watch insight: {text[:100]}... Share with someone who needs this!"
            hooks = [
                f"This changes everything about {self._extract_topic(text)}",
                f"I wish someone told me this about {self._extract_topic(text)} sooner",
                f"The {self._extract_topic(text)} lesson everyone needs to hear",
            ]
            adapted = text
        
        return {
            "original_text": text,
            "adapted_text": adapted,
            "adapted_caption": caption,
            "adapted_hooks": hooks,
            "persona": persona,
            "tone_description": tone,
        }

    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "this", "that", 
                      "and", "but", "or", "for", "to", "in", "on", "at", "by", "of",
                      "i", "you", "we", "they", "it", "not", "so", "if", "do", "have"}
        words = [w for w in text.split()[:20] if w.lower() not in stop_words and len(w) > 2]
        return " ".join(words[:2]).lower() if words else "this"


persona_adapter = PersonaAdapter()
