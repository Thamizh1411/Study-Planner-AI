import datetime
import logging
from typing import Dict, Any, List
from backend.agents.state import PlannerState

logger = logging.getLogger("study_planner_agents")

class SchedulerAgent:
    @staticmethod
    def execute(state: PlannerState) -> PlannerState:
        logger.info("Executing Scheduler Agent...")
        
        # Get inputs
        exam_date_str = state.get("exam_date")
        daily_hours = state.get("daily_hours", 2.0)
        subjects = state.get("subjects", [])
        topics = state.get("topics", [])
        quiz_scores = state.get("quiz_scores", [])
        
        try:
            exam_date = datetime.datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        except Exception:
            exam_date = datetime.date.today() + datetime.timedelta(days=14)
            
        today = datetime.date.today()
        
        # Calculate total days available
        days_until_exam = (exam_date - today).days
        if days_until_exam <= 0:
            days_until_exam = 7  # default window if exam is today or in the past
            
        # Create mapping of subjects for quick difficulty lookup
        subjects_map = {s["name"]: s for s in subjects}
        
        # Determine weak topics (score < 60%) or high error rates
        weak_topics = set()
        topic_scores = {}
        for attempt in quiz_scores:
            t_title = attempt.get("topic_title")
            score = attempt.get("score", 100.0)
            topic_scores[t_title] = score
            if score < 60.0:
                weak_topics.add(t_title)
        
        # Calculate topic weights
        # Higher weights = more hours allocated
        topic_weights = {}
        for topic in topics:
            title = topic.get("title")
            sub_name = topic.get("subject_name")
            confidence = topic.get("confidence", "medium")
            
            # Base weight by subject difficulty
            sub_info = subjects_map.get(sub_name, {"difficulty": "medium"})
            diff = sub_info.get("difficulty", "medium").lower()
            
            if diff == "hard":
                weight = 3.0
            elif diff == "easy":
                weight = 1.0
            else:
                weight = 2.0
                
            # Increase weight for low confidence
            if confidence.lower() == "low":
                weight += 1.5
            elif confidence.lower() == "medium":
                weight += 0.5
                
            # Rebalancing: Increase weight for weak topics based on quiz scores
            if title in weak_topics or topic_scores.get(title, 100.0) < 60.0:
                weight += 2.0  # assign significantly more weight for low quiz scores
                
            topic_weights[title] = weight
            
        # Group topics
        total_weight = sum(topic_weights.values()) or 1.0
        
        # Compute study hours per topic proportional to weights
        # Total study hours available = daily_hours * study_days
        # Let's reserve the last 2 days for final revision
        study_days_count = max(1, days_until_exam - 2)
        total_study_hours_available = daily_hours * study_days_count
        
        topic_hours = {}
        for title, weight in topic_weights.items():
            topic_hours[title] = max(1.0, (weight / total_weight) * total_study_hours_available)
            
        # Distribute study sessions day-by-day
        schedule = {}
        study_days = [today + datetime.timedelta(days=i) for i in range(days_until_exam)]
        
        # Initialize schedule days
        for day in study_days:
            schedule[day.strftime("%Y-%m-%d")] = []
            
        # Allocate topics to days sequentially
        day_index = 0
        for topic in topics:
            title = topic.get("title")
            sub_name = topic.get("subject_name")
            hours_needed = topic_hours.get(title, 2.0)
            
            # We can split hours of a topic across days if it exceeds daily_hours
            while hours_needed > 0:
                if day_index >= study_days_count:
                    # Reset or loop if we run out of study days (pack more items)
                    day_index = day_index % study_days_count
                    
                current_day_str = study_days[day_index].strftime("%Y-%m-%d")
                daily_allocations = schedule[current_day_str]
                
                # Check how many hours already allocated on this day
                allocated_hours = sum(item["hours"] for item in daily_allocations)
                available_today = max(0.5, daily_hours - allocated_hours)
                
                hours_to_alloc = min(hours_needed, available_today)
                if hours_to_alloc > 0:
                    daily_allocations.append({
                        "subject_name": sub_name,
                        "topic_title": title,
                        "hours": round(hours_to_alloc, 1),
                        "type": "study",
                        "completed": False
                    })
                    hours_needed -= hours_to_alloc
                    
                # If day is full, move to next day
                if sum(item["hours"] for item in schedule[current_day_str]) >= daily_hours:
                    day_index += 1
                else:
                    # Even if not full, move to next day to spread topics out
                    day_index += 1
                    
        # SPACING REVISION BLOCKS:
        # Schedule revision sessions for topics.
        # We will add:
        # 1-day revision: 1 day after studying.
        # 3-day revision: 3 days after studying.
        # 7-day revision: 7 days after studying.
        # Let's insert these revision sessions if they fit within our calendar.
        study_days_strs = [d.strftime("%Y-%m-%d") for d in study_days]
        
        for idx, day_str in enumerate(study_days_strs):
            original_studies = [item for item in schedule[day_str] if item["type"] == "study"]
            for study in original_studies:
                t_title = study["topic_title"]
                s_name = study["subject_name"]
                
                # 1 Day Revision
                rev1_idx = idx + 1
                if rev1_idx < study_days_count:
                    r1_day = study_days_strs[rev1_idx]
                    schedule[r1_day].append({
                        "subject_name": s_name,
                        "topic_title": t_title,
                        "hours": 0.5,
                        "type": "revision_1d",
                        "completed": False
                    })
                    
                # 3 Day Revision
                rev3_idx = idx + 3
                if rev3_idx < study_days_count:
                    r3_day = study_days_strs[rev3_idx]
                    schedule[r3_day].append({
                        "subject_name": s_name,
                        "topic_title": t_title,
                        "hours": 0.5,
                        "type": "revision_3d",
                        "completed": False
                    })
                    
                # 7 Day Revision
                rev7_idx = idx + 7
                if rev7_idx < study_days_count:
                    r7_day = study_days_strs[rev7_idx]
                    schedule[r7_day].append({
                        "subject_name": s_name,
                        "topic_title": t_title,
                        "hours": 0.5,
                        "type": "revision_7d",
                        "completed": False
                    })
                    
        # Add Final Revision in the last 2 days before the exam
        final_revision_days = study_days[-2:] if len(study_days) >= 2 else study_days[-1:]
        for f_day in final_revision_days:
            f_day_str = f_day.strftime("%Y-%m-%d")
            # Clear or append to final day study items
            # If final day is already packed, we keep it, but add a 1-hour wrap-up block
            schedule[f_day_str].append({
                "subject_name": "All Subjects",
                "topic_title": "Final Revision & Mock Test Practice",
                "hours": max(1.0, daily_hours),
                "type": "final_revision",
                "completed": False
            })
            
        # Clean up lists: limit items per day to not overflow and sort by type (study then revision)
        for d_str in schedule:
            # Sort: study first, then revision, then final_revision
            schedule[d_str] = sorted(schedule[d_str], key=lambda x: 0 if x["type"] == "study" else (1 if "revision" in x["type"] else 2))
            # Caps the daily allocations if they exceed daily hours by too much (e.g. max daily_hours + 1.5)
            # This handles spacing overlaps cleanly
            daily_total = 0.0
            truncated_items = []
            for item in schedule[d_str]:
                if daily_total + item["hours"] <= daily_hours + 1.5:
                    truncated_items.append(item)
                    daily_total += item["hours"]
            schedule[d_str] = truncated_items
            
        state["schedule"] = schedule
        return state
