"""
AttentionX - Auto Story Builder Service
Combines multiple clips into narrative flows (Problem → Insight → Solution)
"""

import json
from typing import List, Dict
from config import GEMINI_API_KEY
from models.schemas import ViralSegment


class StoryBuilder:
    """
    Builds narrative stories from multiple clips:
    - Problem → Insight → Solution
    - Hook → Build → Payoff
    - Beginning → Middle → End
    """

    NARRATIVE_TEMPLATES = {
        "problem_insight_solution": {
            "structure": ["Problem Statement", "Key Insight", "Solution/Action"],
            "description": "Classic problem-solving narrative",
            "transition_words": ["The problem is...", "But here's the thing...", "So the solution is..."],
        },
        "hook_build_payoff": {
            "structure": ["Attention Hook", "Building Context", "Payoff/Revelation"],
            "description": "Entertainment-style engagement arc",
            "transition_words": ["Wait for it...", "And it gets better...", "Here's the best part..."],
        },
        "before_after": {
            "structure": ["Before State", "Transformation Process", "After State"],
            "description": "Transformation story",
            "transition_words": ["It used to be...", "Then everything changed...", "Now it's..."],
        },
        "myth_reality": {
            "structure": ["Common Myth", "Reality Check", "Truth"],
            "description": "Myth-busting narrative",
            "transition_words": ["Everyone thinks...", "But actually...", "The real truth is..."],
        },
    }

    async def build_story(
        self,
        segments: List[ViralSegment],
        narrative_style: str = "problem_insight_solution",
    ) -> Dict:
        """
        Build a narrative story from selected video segments.
        
        Args:
            segments: List of ViralSegment objects to arrange
            narrative_style: Type of narrative structure
            
        Returns:
            Story dict with title, narrative, order, transitions
        """
        template = self.NARRATIVE_TEMPLATES.get(
            narrative_style, 
            self.NARRATIVE_TEMPLATES["problem_insight_solution"]
        )
        
        # Try AI story building
        ai_story = await self._build_with_ai(segments, narrative_style, template)
        if ai_story:
            return ai_story
        
        # Fallback to rule-based
        return self._build_rule_based(segments, narrative_style, template)

    async def _build_with_ai(
        self, segments: List[ViralSegment], style: str, template: dict
    ) -> Dict:
        """Build story using Gemini AI."""
        if not GEMINI_API_KEY:
            return None
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            segments_text = "\n".join([
                f"Segment {i+1} (ID: {seg.id}, {seg.duration}s, Virality: {seg.virality_score}): {seg.transcript}"
                for i, seg in enumerate(segments)
            ])
            
            prompt = f"""You are a master storyteller for short-form video content.

Given these video segments, arrange them into a compelling "{style}" narrative:

{segments_text}

Narrative structure: {template['structure']}

Tasks:
1. Determine the best order for these segments to tell a story
2. Write transition text between segments
3. Create a compelling title
4. Write a brief narrative description

Return JSON with these exact keys:
{{
    "title": "story title",
    "narrative": "description of how the story flows",
    "segments_order": ["segment_id_1", "segment_id_2", ...],
    "transitions": ["transition before segment 1", "transition between 1-2", ...],
    "story_arc": "description of the emotional arc"
}}

Return ONLY valid JSON, no markdown formatting."""

            response = model.generate_content(prompt)
            
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            
            data = json.loads(text)
            
            total_duration = sum(seg.duration for seg in segments)
            
            return {
                "title": data.get("title", "Untitled Story"),
                "narrative": data.get("narrative", ""),
                "segments_order": data.get("segments_order", [seg.id for seg in segments]),
                "transitions": data.get("transitions", template["transition_words"]),
                "total_duration": round(total_duration, 2),
                "story_arc": data.get("story_arc", template["description"]),
            }
            
        except Exception as e:
            print(f"AI story building error: {e}")
            return None

    def _build_rule_based(
        self, segments: List[ViralSegment], style: str, template: dict
    ) -> Dict:
        """Build story using rule-based approach."""
        if not segments:
            return {
                "title": "No segments available",
                "narrative": "",
                "segments_order": [],
                "transitions": [],
                "total_duration": 0,
                "story_arc": "",
            }
        
        # Sort segments for narrative flow
        ordered = self._arrange_for_narrative(segments, style)
        
        # Generate transitions
        transitions = []
        structure = template["structure"]
        for i, seg in enumerate(ordered):
            if i < len(structure):
                transitions.append(f"[{structure[i]}] {template['transition_words'][min(i, len(template['transition_words'])-1)]}")
            else:
                transitions.append("Continuing the story...")
        
        total_duration = sum(seg.duration for seg in ordered)
        
        # Generate title from content
        title = self._generate_title(ordered, style)
        
        return {
            "title": title,
            "narrative": f"A {template['description']} built from {len(ordered)} key moments.",
            "segments_order": [seg.id for seg in ordered],
            "transitions": transitions,
            "total_duration": round(total_duration, 2),
            "story_arc": template["description"],
        }

    def _arrange_for_narrative(
        self, segments: List[ViralSegment], style: str
    ) -> List[ViralSegment]:
        """Arrange segments to fit narrative style."""
        if len(segments) <= 1:
            return segments
        
        if style == "problem_insight_solution":
            # Lower virality first (problem), then insight, then highest (solution)
            sorted_segs = sorted(segments, key=lambda s: s.virality_score)
            # Take first, middle, last
            if len(sorted_segs) >= 3:
                return [sorted_segs[0], sorted_segs[len(sorted_segs)//2], sorted_segs[-1]]
            return sorted_segs
            
        elif style == "hook_build_payoff":
            # Highest virality first (hook), medium build, high payoff
            sorted_segs = sorted(segments, key=lambda s: s.virality_score, reverse=True)
            if len(sorted_segs) >= 3:
                return [sorted_segs[0], sorted_segs[-1], sorted_segs[1]]
            return sorted_segs
            
        elif style == "before_after":
            # Chronological order
            return sorted(segments, key=lambda s: s.start)
            
        else:
            # Default: chronological
            return sorted(segments, key=lambda s: s.start)

    def _generate_title(self, segments: List[ViralSegment], style: str) -> str:
        """Generate a title from segment content."""
        if not segments:
            return "Untitled Story"
        
        # Use the highest virality segment for title inspiration
        best = max(segments, key=lambda s: s.virality_score)
        words = best.transcript.split()[:8]
        
        if style == "problem_insight_solution":
            return f"The Truth About {' '.join(words[:3]).title()}"
        elif style == "hook_build_payoff":
            return f"You Won't Believe: {' '.join(words[:4]).title()}"
        elif style == "before_after":
            return f"The {' '.join(words[:3]).title()} Transformation"
        else:
            return f"{' '.join(words[:5]).title()}..."


story_builder = StoryBuilder()
