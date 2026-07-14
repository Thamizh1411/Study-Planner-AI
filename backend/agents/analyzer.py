import json
import logging
from backend.agents.state import PlannerState
from backend.agents.providers import LLMProvider

logger = logging.getLogger("study_planner_agents")

class PerformanceAnalyzerAgent:
    @staticmethod
    def execute(state: PlannerState) -> PlannerState:
        logger.info("Executing Performance Analyzer Agent...")
        
        quiz_scores = state.get("quiz_scores", [])
        topics = state.get("topics", [])
        schedule = state.get("schedule", {})
        
        # Calculate completion rate
        total_topics = len(topics)
        completed_topics = len([t for t in topics if t.get("status") == "completed"])
        completion_rate = (completed_topics / total_topics * 100.0) if total_topics > 0 else 0.0
        
        # Calculate study hours and skipped days
        total_hours_scheduled = 0.0
        total_hours_completed = 0.0
        skipped_days = 0
        
        for date_str, items in schedule.items():
            day_scheduled = sum(item.get("hours", 0.0) for item in items)
            day_completed = sum(item.get("hours", 0.0) for item in items if item.get("completed", False))
            
            total_hours_scheduled += day_scheduled
            total_hours_completed += day_completed
            
            if day_scheduled > 0 and day_completed == 0:
                skipped_days += 1
                
        # Calculate quiz performance
        quiz_count = len(quiz_scores)
        average_score = sum(q.get("score", 0.0) for q in quiz_scores) / quiz_count if quiz_count > 0 else 0.0
        
        # Identify weak topics
        weak_topics = []
        topic_scores = {}
        for attempt in quiz_scores:
            title = attempt.get("topic_title")
            score = attempt.get("score", 0.0)
            topic_scores.setdefault(title, []).append(score)
            
        for title, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 60.0:
                weak_topics.append({"topic_title": title, "average_score": round(avg, 1)})
                
        # Calculate base scores
        productivity_score = 100.0
        if total_hours_scheduled > 0:
            productivity_score = min(100.0, (total_hours_completed / total_hours_scheduled) * 100.0)
        # Deduct for skipped days
        productivity_score = max(0.0, productivity_score - (skipped_days * 5.0))
        
        learning_score = 50.0
        if quiz_count > 0:
            learning_score = average_score
        # Boost based on completion rate
        learning_score = round(min(100.0, learning_score * 0.7 + completion_rate * 0.3), 1)
        
        # Ask LLM to generate the report content
        system_prompt = (
            "You are an expert Performance Analyzer Agent. Your job is to analyze study patterns, "
            "quiz logs, and schedules, and output a structured performance report with suggestions."
        )
        
        prompt = f"""
        Analyze the following student performance stats and generate a report:
        - Topic Completion Rate: {completion_rate:.1f}%
        - Study Hours: Completed {total_hours_completed:.1f} out of {total_hours_scheduled:.1f} hours scheduled
        - Skipped Days: {skipped_days}
        - Average Quiz Score: {average_score:.1f}%
        - Weak Topics: {weak_topics}
        - Calculated Productivity Score: {productivity_score:.1f}/100
        - Calculated Learning Score: {learning_score:.1f}/100
        
        Generate a JSON report structure containing:
        1. "weekly_summary": A detailed summary paragraph analyzing the student's study consistency and academic progress.
        2. "suggestions": A list of 3-4 actionable tips to improve learning efficiency, weak topic mastery, or schedule alignment.
        3. "productivity_badge": A gamified streak/achievement label based on productivity (e.g. "Consistent Scholar", "Streak Booster", "Focus Rookie").
        
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
                
            report_data = json.loads(response_str)
        except Exception as e:
            logger.error(f"Failed to generate performance analyzer report: {str(e)}")
            report_data = {
                "weekly_summary": "Your study habits are starting to stabilize. Keep pushing to complete planned hours on schedule and review notes before quizzes.",
                "suggestions": [
                    "Allocate specific blocks of quiet time for your hard subjects.",
                    "Review flashcards daily for topics with lower confidence levels.",
                    "Practice coding syntax repeatedly before taking the coding quizzes."
                ],
                "productivity_badge": "Focus Explorer"
            }
            
        # Combine programmatic results and LLM reports
        state["analysis"] = {
            "completion_rate": round(completion_rate, 1),
            "total_hours_scheduled": round(total_hours_scheduled, 1),
            "total_hours_completed": round(total_hours_completed, 1),
            "skipped_days": skipped_days,
            "average_quiz_score": round(average_score, 1),
            "weak_topics": weak_topics,
            "productivity_score": round(productivity_score, 1),
            "learning_score": round(learning_score, 1),
            "weekly_summary": report_data.get("weekly_summary"),
            "suggestions": report_data.get("suggestions"),
            "productivity_badge": report_data.get("productivity_badge")
        }
        
        return state
