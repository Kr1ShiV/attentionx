"""
AttentionX - Content Remix Engine
Converts clips into platform-optimized formats (Instagram, YouTube, LinkedIn, TikTok)
"""

import json
from typing import Dict, List
from config import GEMINI_API_KEY, PLATFORM_SPECS


class RemixEngine:
    """
    Remixes content for different social media platforms:
    - Instagram Reel: Visual, punchy, trend-aware
    - YouTube Short: Informative, searchable, value-packed
    - LinkedIn Post: Professional, storytelling, text-based
    - TikTok: Raw, authentic, hook-heavy
    """

    def __init__(self):
        self.specs = PLATFORM_SPECS

    async def remix(
        self,
        text: str,
        platform: str,
    ) -> Dict:
        """
        Remix content for a specific platform.
        
        Args:
            text: Original transcript/content
            platform: Target platform
            
        Returns:
            Dict with platform-optimized content
        """
        spec = self.specs.get(platform, self.specs["instagram_reel"])
        
        # Try AI remix
        ai_result = await self._remix_with_ai(text, platform, spec)
        if ai_result:
            return ai_result
        
        # Fallback to rule-based
        return self._remix_rule_based(text, platform, spec)

    async def _remix_with_ai(self, text: str, platform: str, spec: dict) -> Dict:
        """Remix using Gemini AI."""
        if not GEMINI_API_KEY:
            return None
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            platform_name = platform.replace("_", " ").title()
            
            prompt = f"""You are a multi-platform content strategist.

Remix this video content for {platform_name}:

ORIGINAL CONTENT:
"{text}"

PLATFORM SPECS:
- Style: {spec['style']}
- Max caption length: {spec['max_caption_length']} chars
- Hashtag count: {spec['hashtag_count']}
{f"- Max duration: {spec['max_duration']}s" if spec.get('max_duration') else "- Format: Text post"}
{f"- Aspect ratio: {spec.get('aspect_ratio', 'N/A')}" if spec.get('aspect_ratio') else ""}

TASKS:
1. Rewrite the content optimized for this specific platform
2. Write the perfect caption
3. Generate relevant hashtags
4. Specify format details

Return JSON:
{{
    "content": "platform-optimized content/script",
    "caption": "platform caption",
    "hashtags": ["hashtag1", "hashtag2", ...],
    "format_specs": {{
        "recommended_length": "duration or word count",
        "visual_style": "recommended visual treatment",
        "cta": "call to action text"
    }}
}}

Return ONLY valid JSON."""

            response = model.generate_content(prompt)
            
            resp_text = response.text.strip()
            if resp_text.startswith("```"):
                resp_text = resp_text.split("\n", 1)[1].rsplit("```", 1)[0]
            
            data = json.loads(resp_text)
            
            content = data.get("content", text)
            caption = data.get("caption", "")
            
            return {
                "platform": platform,
                "content": content,
                "caption": caption[:spec["max_caption_length"]],
                "hashtags": data.get("hashtags", [])[:spec["hashtag_count"]],
                "format_specs": data.get("format_specs", {}),
                "character_count": len(caption),
            }
            
        except Exception as e:
            print(f"AI remix error: {e}")
            return None

    def _remix_rule_based(self, text: str, platform: str, spec: dict) -> Dict:
        """Rule-based content remix."""
        content = text
        caption = ""
        hashtags = []
        format_specs = {}
        
        if platform == "instagram_reel":
            # Short, punchy, visual-first
            sentences = text.split(".")
            content = ". ".join(sentences[:3]) + "." if sentences else text
            caption = f"🔥 {sentences[0].strip() if sentences else text[:100]}\n\n💡 Save this for later!\n\n"
            hashtags = ["#reels", "#viral", "#trending", "#motivation", "#learn", 
                       "#growth", "#mindset", "#success", "#tips", "#knowledge",
                       "#instagood", "#explorepage", "#fyp", "#educational", "#wisdom"]
            format_specs = {
                "recommended_length": "15-30 seconds",
                "visual_style": "Quick cuts, bold text overlays, trending audio",
                "cta": "Follow for more insights like this! 🚀",
            }
            
        elif platform == "youtube_short":
            content = text
            caption = f"🎯 {text[:200]}...\n\n📌 Subscribe for daily insights!"
            hashtags = ["#shorts", "#youtubeshorts", "#learning", "#education", "#tips"]
            format_specs = {
                "recommended_length": "30-60 seconds",
                "visual_style": "Talking head with key points as text overlay",
                "cta": "Subscribe and hit the bell! 🔔",
            }
            
        elif platform == "linkedin_post":
            # Professional storytelling format
            sentences = text.split(".")
            story_lines = []
            story_lines.append(f"I had a realization about {self._extract_topic(text)}.\n")
            for i, s in enumerate(sentences[:5]):
                if s.strip():
                    story_lines.append(f"{s.strip()}.")
            story_lines.append(f"\n💡 The key takeaway?")
            story_lines.append(f"\n{sentences[-1].strip() if sentences else 'This changes everything.'}")
            story_lines.append(f"\n---\n♻️ Repost if you agree\n💬 What are your thoughts?")
            
            content = "\n\n".join(story_lines)
            caption = content
            hashtags = ["#leadership", "#innovation", "#learning", "#growth", "#career"]
            format_specs = {
                "recommended_length": "150-300 words",
                "visual_style": "Text post with line breaks, use ↳ for points",
                "cta": "♻️ Repost to share with your network",
            }
            
        elif platform == "tiktok":
            sentences = text.split(".")
            content = ". ".join(sentences[:2]) + "." if sentences else text[:150]
            caption = f"{text[:100]}... 🤯 #fyp"
            hashtags = ["#fyp", "#foryou", "#viral", "#learn", "#mindblown"]
            format_specs = {
                "recommended_length": "15-30 seconds",
                "visual_style": "Raw, authentic, face-to-camera, trending sound",
                "cta": "Follow for Part 2! 👆",
            }
        
        return {
            "platform": platform,
            "content": content,
            "caption": caption[:spec["max_caption_length"]],
            "hashtags": hashtags[:spec["hashtag_count"]],
            "format_specs": format_specs,
            "character_count": len(caption),
        }

    def _extract_topic(self, text: str) -> str:
        """Extract main topic."""
        stop = {"the", "a", "an", "is", "are", "was", "to", "in", "on", "of", "and", "i", "you", "we"}
        words = [w for w in text.split()[:15] if w.lower() not in stop and len(w) > 2]
        return " ".join(words[:3]).lower() if words else "this"

    async def remix_all_platforms(self, text: str) -> Dict[str, Dict]:
        """Remix content for all platforms at once."""
        results = {}
        for platform in self.specs:
            results[platform] = await self.remix(text, platform)
        return results


remix_engine = RemixEngine()
