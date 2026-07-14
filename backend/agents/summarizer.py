import logging
from backend.agents.state import PlannerState
from backend.agents.providers import LLMProvider

logger = logging.getLogger("study_planner_agents")

class SummarizerAgent:
    @staticmethod
    def execute(state: PlannerState) -> PlannerState:
        logger.info("Executing Summarizer Agent...")
        notes = state.get("notes") or {}
        research_data = state.get("research_data") or {}
        
        for title, data in research_data.items():
            if title in notes:
                continue
                
            logger.info(f"Summarizing topic: {title}")
            
            system_prompt = (
                "You are an expert Summarizer Agent. Your job is to convert detailed research data "
                "into concise, high-quality, and easy-to-read student study notes. "
                "You must output clean, beautifully structured Markdown format only. Do not include any HTML."
            )
            
            prompt = f"""
            Generate student study notes for the following researched topic details:
            
            Topic: {title}
            Explanation: {data.get("explanation", "")}
            Formulas: {", ".join(data.get("formulas", []))}
            Examples: {data.get("examples", [])}
            
            Your markdown notes should follow this strict structure:
            1. # [Topic Title] - Core Summary
            2. ## Key Concepts (using bullet points)
            3. ## Important Definitions (defining key terms clearly)
            4. ## Formulas & Key Rules (if any)
            5. ## Practical Examples (step-by-step)
            6. ## Memory Tricks & Mnemonics (creative tips to remember these concepts)
            7. ## External Resources (list reference links from the research details)
            
            Keep the content engaging, readable, and highly organized for exam preparation.
            """
            
            try:
                # Fast-mode heuristic: if a caller caps topic count, we may want to skip one expensive LLM call.
                # Use env toggle to disable summarizer LLM calls.
                import os
                if os.getenv("PLAN_DISABLE_SUMMARIZER_LLM", "false").lower() in ("1", "true", "yes"):
                    raise RuntimeError("Summarizer LLM disabled by PLAN_DISABLE_SUMMARIZER_LLM")

                markdown_notes = LLMProvider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    json_mode=False,
                )
                notes[title] = markdown_notes.strip()
            except Exception as e:
                logger.error(f"Failed to generate summary for {title}: {str(e)}")
                # Provide a basic fallback markdown summary
                notes[title] = f"""
# {title} - Core Summary

## Key Concepts
- Concept overview of {title}.
- Focus on foundation parameters and core principles.

## Important Definitions
- **{title}**: General study topic area.

## Formulas & Key Rules
- No standard formula defined. Refer to general textbooks.

## Practical Examples
- Standard study case studies in class lectures.

## Memory Tricks & Mnemonics
- Remember: **B.A.S.I.C.** (Build understanding, Analyze elements, Solve examples, Integrate context, Confirm results).
"""
                
        state["notes"] = notes
        return state
