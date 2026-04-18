"""
AttentionX - Hook Generator Engine
Generates viral hooks for video clips using AI and pattern templates
"""

import json
import random
from typing import List
from config import GEMINI_API_KEY


class HookGenerator:
    """
    Generates viral hooks for clips using:
    - Pattern-based templates
    - AI-powered custom hooks via Gemini
    """

    HOOK_PATTERNS = {
        "curiosity": [
            "Nobody tells you this about {topic}…",
            "The {topic} secret that changed everything",
            "I spent {time} studying {topic}. Here's what I found.",
            "What they don't teach you about {topic}",
            "The hidden truth about {topic} that experts won't share",
            "This one {topic} insight will change how you think",
        ],
        "shock": [
            "This mistake cost me {consequence}",
            "STOP doing this with {topic} immediately",
            "I was wrong about {topic} for years",
            "The {topic} myth everyone still believes",
            "{topic} is broken. Here's proof.",
            "I can't believe {topic} actually works this way",
        ],
        "challenge": [
            "If you're doing {topic}, STOP",
            "Try this {topic} method for 30 days",
            "I dare you to {action} for one week",
            "Most people can't handle this {topic} truth",
            "Are you making this {topic} mistake?",
            "You're probably wrong about {topic}. Here's why.",
        ],
        "story": [
            "How I went from {before} to {after}",
            "The {topic} story nobody talks about",
            "What happened when I tried {action}",
            "From {before} to {after}: the {topic} journey",
            "The moment everything changed with {topic}",
            "A {topic} lesson I'll never forget",
        ],
        "value": [
            "3 {topic} tips that actually work",
            "The ultimate guide to {topic} in 60 seconds",
            "{topic} explained in the simplest way possible",
            "Save this {topic} hack for later",
            "The only {topic} advice you need",
            "Master {topic} with this simple framework",
        ],
    }

    async def generate_hooks(
        self,
        text: str,
        style: str = "curiosity",
        count: int = 3
    ) -> List[str]:
        """
        Generate viral hooks for a text segment.
        
        Args:
            text: The transcript text of the segment
            style: Hook style (curiosity, shock, challenge, story, value)
            count: Number of hooks to generate
        """
        hooks = []
        
        # Try AI-generated hooks first
        ai_hooks = await self._generate_ai_hooks(text, style, count)
        if ai_hooks:
            hooks.extend(ai_hooks)
        
        # Fill with pattern-based hooks if needed
        if len(hooks) < count:
            pattern_hooks = self._generate_pattern_hooks(text, style, count - len(hooks))
            hooks.extend(pattern_hooks)
        
        return hooks[:count]

    async def _generate_ai_hooks(
        self, text: str, style: str, count: int
    ) -> List[str]:
        """Generate hooks using Gemini AI."""
        if not GEMINI_API_KEY:
            return []
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            style_descriptions = {
                "curiosity": "curiosity-driven hooks that make viewers NEED to know more",
                "shock": "shocking, contrarian hooks that challenge expectations",
                "challenge": "challenge-based hooks that dare the viewer to act",
                "story": "story-based hooks that pull viewers into a narrative",
                "value": "value-packed hooks promising quick, actionable insights",
            }
            
            prompt = f"""You are a viral content strategist. Generate exactly {count} scroll-stopping hooks 
for a short-form video clip based on this content:

"{text}"

Style: {style_descriptions.get(style, style_descriptions['curiosity'])}

Rules:
- Each hook must be 5-15 words
- Must create immediate curiosity or emotional response
- Use power words and psychological triggers
- Make the viewer UNABLE to scroll past
- No emojis in the hooks themselves
- Each hook on a new line, numbered 1-{count}

Return ONLY the numbered hooks, nothing else."""

            response = model.generate_content(prompt)
            
            hooks = []
            for line in response.text.strip().split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    # Remove number prefix
                    hook = line.split(".", 1)[-1].strip() if "." in line else line
                    hook = hook.split(")", 1)[-1].strip() if ")" in hook else hook
                    hook = hook.strip('"').strip("'")
                    if hook:
                        hooks.append(hook)
            
            return hooks[:count]
            
        except Exception as e:
            print(f"AI hook generation error: {e}")
            return []

    def _generate_pattern_hooks(
        self, text: str, style: str, count: int
    ) -> List[str]:
        """Generate hooks using pattern templates."""
        patterns = self.HOOK_PATTERNS.get(style, self.HOOK_PATTERNS["curiosity"])
        
        # Extract topic from text
        topic = self._extract_topic(text)
        
        hooks = []
        selected = random.sample(patterns, min(count, len(patterns)))
        
        for pattern in selected:
            hook = pattern.format(
                topic=topic,
                time="6 months",
                consequence="everything",
                before="struggling",
                after="thriving",
                action=f"applying this to {topic}",
            )
            hooks.append(hook)
        
        return hooks

    def _extract_topic(self, text: str) -> str:
        """Extract the main topic from text."""
        # Simple extraction: find the most significant noun phrase
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "shall",
            "this", "that", "these", "those", "i", "you", "he", "she",
            "it", "we", "they", "me", "him", "her", "us", "them", "my",
            "your", "his", "its", "our", "their", "and", "but", "or",
            "so", "if", "then", "than", "too", "very", "just", "about",
            "up", "out", "in", "on", "off", "over", "under", "again",
            "to", "from", "with", "at", "by", "for", "of", "not", "no",
        }
        
        meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        
        if meaningful:
            # Take first 2-3 meaningful words as topic
            return " ".join(meaningful[:3]).lower()
        
        return "this"

    async def generate_all_styles(self, text: str) -> dict:
        """Generate hooks in all styles for comparison."""
        results = {}
        for style in self.HOOK_PATTERNS.keys():
            hooks = await self.generate_hooks(text, style, count=2)
            results[style] = hooks
        return results


hook_generator = HookGenerator()
