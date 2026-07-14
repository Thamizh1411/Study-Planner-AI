from langgraph.graph import StateGraph, START, END
from backend.agents.state import PlannerState
from backend.agents.researcher import ResearchAgent
from backend.agents.summarizer import SummarizerAgent
from backend.agents.quiz_generator import QuizGeneratorAgent
from backend.agents.scheduler import SchedulerAgent
from backend.agents.analyzer import PerformanceAnalyzerAgent
from backend.agents.motivator import MotivationAgent

# Initialize graph
workflow = StateGraph(PlannerState)

# Register node handlers
workflow.add_node("researcher", ResearchAgent.execute)
workflow.add_node("summarizer", SummarizerAgent.execute)
workflow.add_node("quiz_generator", QuizGeneratorAgent.execute)
workflow.add_node("scheduler", SchedulerAgent.execute)
workflow.add_node("analyzer", PerformanceAnalyzerAgent.execute)
workflow.add_node("motivator", MotivationAgent.execute)

# Define transitions
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "summarizer")
workflow.add_edge("summarizer", "quiz_generator")
workflow.add_edge("quiz_generator", "scheduler")
workflow.add_edge("scheduler", "analyzer")
workflow.add_edge("analyzer", "motivator")
workflow.add_edge("motivator", END)

# Compile graph
planner_graph = workflow.compile()
