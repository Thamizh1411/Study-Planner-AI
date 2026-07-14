import json
import logging
from backend.agents.state import PlannerState
from backend.agents.providers import LLMProvider

logger = logging.getLogger("study_planner_agents")

class MotivationAgent:
    @staticmethod
    def execute(state: PlannerState) -> PlannerState:
        logger.info("Executing Motivation Agent...")
        
        analysis = state.get("analysis") or {}
        prod_score = analysis.get("productivity_score", 100.0)
        learn_score = analysis.get("learning_score", 50.0)
        
        system_prompt = (
            "You are an inspiring, supportive Motivation Agent. Your job is to encourage students, "
            "recommend healthy study routines (Pomodoro, break limits), and help manage stress. "
            "You must output structured JSON ONLY. Do not include markdown wraps."
        )
        
        prompt = f"""
        Generate motivational guidance for a student with the following profile scores:
        - Productivity score: {prod_score:.1f}/100
        - Learning score: {learn_score:.1f}/100
        
        Provide a JSON object containing:
        1. "daily_motivation": A short, energetic, inspiring motivational quote or direct encouragement statement.
        2. "study_tips": A list of 2 specific, actionable methods to retain information better (e.g. Feyman technique, active recall).
        3. "pomodoro_suggestion": A recommended work/break interval suited for their scores (e.g. 25/5 or 50/10).
        4. "break_reminder": Advice on what to do during study breaks to rest the eyes and brain.
        5. "stress_management": Actionable advice on staying calm and avoiding burnout during exams.
        
        Output valid JSON only.
        """
        
        try:
            response_str = LLMProvider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            # Clean response
            response_str = response_str.strip()
            if response_str.startswith("```"):
                lines = response_str.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                response_str = "\n".join(lines).strip()
                
            motivation_data = json.loads(response_str)
        except Exception as e:
            logger.error(f"Failed to generate motivation content: {str(e)}")
            motivation_data = {
                "daily_motivation": "Believe you can and you're halfway there. Consistency is key!",
                "study_tips": [
                    "Use active recall: close your notebook and explain the topic aloud.",
                    "Feynman Technique: write explanations as if teaching a beginner."
                ],
                "pomodoro_suggestion": "Study for 25 minutes, then take a 5-minute break.",
                "break_reminder": "Step away from your screen. Stretch, grab water, or walk outside.",
                "stress_management": "Take 3 deep belly breaths when feeling overwhelmed. Prioritize sleep."
            }
            
        state["motivation"] = motivation_data
        return state
