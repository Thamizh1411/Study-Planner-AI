import json
import logging
from backend.agents.state import PlannerState
from backend.agents.providers import LLMProvider

logger = logging.getLogger("study_planner_agents")

class QuizGeneratorAgent:
    @staticmethod
    def execute(state: PlannerState) -> PlannerState:
        logger.info("Executing Quiz Generator Agent...")
        quizzes = state.get("quizzes") or {}
        notes = state.get("notes") or {}
        quiz_scores = state.get("quiz_scores") or []
        subjects_map = {s["name"]: s for s in state.get("subjects", [])}
        topics = state.get("topics", [])
        
        for topic in topics:
            title = topic.get("title")
            sub_name = topic.get("subject_name")
            
            if title in quizzes:
                # Quiz already exists, skip regenerating unless explicitly requested.
                continue
                
            summary_content = notes.get(title, "Basic concept study details.")
            
            # Determine baseline difficulty
            subject_info = subjects_map.get(sub_name, {"difficulty": "medium"})
            base_difficulty = subject_info.get("difficulty", "medium")
            
            # ADAPTIVE DIFFICULTY: Check prior quiz scores for this topic
            prior_scores = [q.get("score", 0.0) for q in quiz_scores if q.get("topic_title") == title]
            
            difficulty = base_difficulty
            if prior_scores:
                last_score = prior_scores[-1]
                if last_score >= 80.0:
                    if base_difficulty == "easy":
                        difficulty = "medium"
                    elif base_difficulty == "medium":
                        difficulty = "hard"
                elif last_score < 50.0:
                    if base_difficulty == "hard":
                        difficulty = "medium"
                    elif base_difficulty == "medium":
                        difficulty = "easy"
            
            logger.info(f"Generating quiz for topic: {title} (Difficulty: {difficulty})")
            
            system_prompt = (
                "You are an expert Quiz Generator Agent. Your job is to create challenging, educational quiz questions "
                "based on study summaries. You must output structured JSON ONLY. Do not include markdown wraps."
            )
            
            prompt = f"""
            Generate a comprehensive quiz for the topic: {title}
            Difficulty Level: {difficulty}
            Context/Summary Notes:
            \"\"\"{summary_content}\"\"\"
            
            You must output a JSON list of exactly 5 questions.
            Each question must have the following fields:
            1. "id": uniquely numbered (1 to 5)
            2. "question_text": The clear question text.
            3. "type": One of: "mcq", "true_false", "fill_blank", "short_answer", "coding"
            4. "options": List of 4 string options (Only applicable and required if type is "mcq")
            5. "correct_answer": The correct answer (string format). For short_answer or coding, provide a concise solution keyword or expected output.
            6. "points": numerical point weight (e.g. 10)
            7. "difficulty": "{difficulty}"
            
            Include:
            - 1 MCQ
            - 1 True/False
            - 1 Fill in the blanks
            - 1 Short Answer
            - 1 Coding Question (or deep analytical question if not a coding subject)
            
            Output format MUST be a pure JSON array of objects.
            """
            
            try:
                response_str = LLMProvider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    json_mode=True
                )
                
                # Clean markdown tags
                response_str = response_str.strip()
                if response_str.startswith("```"):
                    lines = response_str.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    response_str = "\n".join(lines).strip()
                    
                questions = json.loads(response_str)
                quizzes[title] = {
                    "topic_title": title,
                    "difficulty": difficulty,
                    "questions": questions
                }
            except Exception as e:
                logger.error(f"Failed to generate quiz for {title}: {str(e)}")
                # Provide standard fallback quiz
                quizzes[title] = {
                    "topic_title": title,
                    "difficulty": difficulty,
                    "questions": [
                        {
                            "id": 1,
                            "question_text": f"What is the main concept of {title}?",
                            "type": "mcq",
                            "options": ["A key foundation", "A minor variable", "An irrelevant topic", "None of the above"],
                            "correct_answer": "A key foundation",
                            "points": 10,
                            "difficulty": difficulty
                        },
                        {
                            "id": 2,
                            "question_text": f"True or False: Understanding {title} is critical for exam success.",
                            "type": "true_false",
                            "options": [],
                            "correct_answer": "True",
                            "points": 10,
                            "difficulty": difficulty
                        },
                        {
                            "id": 3,
                            "question_text": f"{title} acts as a core ________ for solving subject problems.",
                            "type": "fill_blank",
                            "options": [],
                            "correct_answer": "foundation",
                            "points": 10,
                            "difficulty": difficulty
                        },
                        {
                            "id": 4,
                            "question_text": f"Briefly explain the primary goal of studying {title}.",
                            "type": "short_answer",
                            "options": [],
                            "correct_answer": "To master the foundational subject principles and applications.",
                            "points": 10,
                            "difficulty": difficulty
                        },
                        {
                            "id": 5,
                            "question_text": f"Write a simple pseudo-code/expression showing how you would evaluate {title} variables.",
                            "type": "coding",
                            "options": [],
                            "correct_answer": "def evaluate_concept(x): return x * 2",
                            "points": 10,
                            "difficulty": difficulty
                        }
                    ]
                }
                
        state["quizzes"] = quizzes
        return state
