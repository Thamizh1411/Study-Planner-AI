# TODO - Timeout fixes for Study Planner AI

## Step 1 (Investigate & confirm)
- [x] Inspect LangGraph pipeline and LLM call counts per topic.
- [x] Confirm `LLMProvider` default timeout (25s) and retries (1).

## Step 2 (Implement)
- [ ] Add `current_user` dependency fix in `backend/api/ai.py` for generate-plan.
- [ ] Add topic cap (process top-K topics) inside `generate_study_plan`.
- [ ] Add per-call timeout override + “fast mode” in `LLMProvider.generate()`.
- [ ] Add summarizer fallback-template mode to reduce one LLM call per topic.
- [ ] Add overall time budgeting around `planner_graph.invoke()`; on timeout, return partial results.
- [ ] Run backend and test endpoints to ensure timeout no longer occurs.


## Step 3 (Test)
- [ ] Run backend and call `/api/v1/ai/chat-tutor` and `/api/v1/ai/generate-plan/{exam_id}`.
- [ ] Verify responses return (no 504) and contain schedule + partial notes/quizzes.

