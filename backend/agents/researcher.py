import json
import logging
from backend.agents.state import PlannerState
from backend.agents.providers import LLMProvider

logger = logging.getLogger("study_planner_agents")

class ResearchAgent:
    @staticmethod
    def execute(state: PlannerState) -> PlannerState:
        logger.info("Executing Research Agent...")
        research_data = state.get("research_data") or {}
        
        # We will research any topic that doesn't have research data yet
        topics = state.get("topics", [])
        subjects_map = {s["name"]: s for s in state.get("subjects", [])}
        
        for topic in topics:
            title = topic.get("title")
            sub_name = topic.get("subject_name")
            
            if title in research_data:
                continue
                
            subject_info = subjects_map.get(sub_name, {"difficulty": "medium"})
            difficulty = subject_info.get("difficulty", "medium")
            confidence = topic.get("confidence", "medium")
            
            logger.info(f"Researching topic: {title} (Subject: {sub_name}, Difficulty: {difficulty})")
            
            system_prompt = (
                "You are an expert Research Agent. Your job is to search reliable academic resources "
                "and find explanations, mathematical formulas, detailed examples, and real reference links (like Wikipedia, LibreTexts, Khan Academy, etc.). "
                "You must output structured JSON ONLY. Do not include any markdown formatting like ```json or trailing text. The output must be pure JSON."
            )
            
            prompt = f"""
            Research the following academic topic:
            Topic Title: {title}
            Subject: {sub_name}
            Target Difficulty: {difficulty}
            Student Current Confidence: {confidence}
            
            Provide a JSON object containing:
            1. "topic_title": The topic title.
            2. "explanation": A detailed, clear academic explanation of the core concepts of this topic.
            3. "formulas": A list of important mathematical formulas, chemical equations, or fundamental rules (as LaTeX or plain text) relevant to this topic. If none exist, output an empty list.
            4. "examples": A list of concrete, step-by-step examples or case studies explaining the concepts.
            5. "reference_links": A list of active, reliable educational resources/reference URLs (e.g., wikipedia.org, khanacademy.org, geeksforgeeks.org, wolframalpha.com) with a title and brief description for each.
            
            Example Format:
            {{
                "topic_title": "Topic Name",
                "explanation": "...",
                "formulas": ["...", "..."],
                "examples": ["...", "..."],
                "reference_links": [
                    {{"title": "Wikipedia - Topic Name", "url": "https://en.wikipedia.org/wiki/...", "description": "Overview of..."}}
                ]
            }}
            """
            
            try:
                response_str = LLMProvider.generate(
                    prompt=prompt, 
                    system_prompt=system_prompt, 
                    json_mode=True
                )
                
                # Clean response string in case LLM added markdown tags
                response_str = response_str.strip()
                if response_str.startswith("```"):
                    # remove leading and trailing markdown block if present
                    lines = response_str.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    response_str = "\n".join(lines).strip()
                    
                data = json.loads(response_str)
                research_data[title] = data
            except Exception as e:
                logger.error(f"Failed to research topic {title}: {str(e)}")
                # Provide standard fallback JSON so we don't break the graph execution
                research_data[title] = {
                    "topic_title": title,
                    "explanation": f"Basic review details for {title} (Subject: {sub_name}). Concept focuses on key terminology and standard definitions.",
                    "formulas": [],
                    "examples": [f"Standard textbook applications of {title} in study domains."],
                    "reference_links": [
                        {"title": "Wikipedia Search", "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}", "description": "Search references for general overview."}
                    ]
                }
                
        state["research_data"] = research_data
        return state
