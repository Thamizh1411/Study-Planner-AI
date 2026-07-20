from langgraph.graph import StateGraph, START, END
from backend.agents.state import PlannerState
from backend.agents.researcher import ResearchAgent
from backend.agents.summarizer import SummarizerAgent
from backend.agents.quiz_generator import QuizGeneratorAgent
from backend.agents.scheduler import SchedulerAgent
from backend.agents.analyzer import PerformanceAnalyzerAgent
from backend.agents.motivator import MotivationAgent

workflow = StateGraph(PlannerState)

NODES = (
    ("researcher", ResearchAgent.execute),
    ("summarizer", SummarizerAgent.execute),
    ("quiz_generator", QuizGeneratorAgent.execute),
    ("scheduler", SchedulerAgent.execute),
    ("analyzer", PerformanceAnalyzerAgent.execute),
    ("motivator", MotivationAgent.execute),
)

for node_name, handler in NODES:
    workflow.add_node(node_name, handler)

EDGES = (
    (START, "researcher"),
    ("researcher", "summarizer"),
    ("summarizer", "quiz_generator"),
    ("quiz_generator", "scheduler"),
    ("scheduler", "analyzer"),
    ("analyzer", "motivator"),
    ("motivator", END),
)

for source, destination in EDGES:
    workflow.add_edge(source, destination)

planner_graph = workflow.compile()
