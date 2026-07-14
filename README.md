# Study Planner AI - Multi-Agent Study Planner SaaS

Study Planner AI is an industry-level, production-ready full-stack SaaS application that creates personalized, dynamically rebalancing study plans for students. 

The application utilizes a **Multi-Agent Architecture** running on **LangGraph** in the backend (FastAPI), with a Streamlit-based frontend interface for student study planning.

---

## Architecture Overview

The system is built on a **cooperative multi-agent state transition graph** compiling six specialized workers:

```mermaid
graph TD
    Start([Start Planning]) --> Worker1[1. Research Agent]
    Worker1 --> |Collects Context| Worker2[2. Summarizer Agent]
    Worker2 --> |Compiles Markdown| Worker3[3. Quiz Maker Agent]
    Worker3 --> |Designs Q&As| Worker4[4. Scheduler Agent]
    Worker4 --> |Creates Timetable| Worker5[5. Performance Analyzer]
    Worker5 --> |Builds Metrics| Worker6[6. Motivation Agent]
    Worker6 --> |Injects Inspiration| End([End Compilation])
    
    style Start fill:#1d4ed8,stroke:#3b82f6,color:#fff
    style End fill:#1e1b4b,stroke:#a855f7,color:#fff
    style Worker4 fill:#0f766e,stroke:#14b8a6,color:#fff
    style Worker5 fill:#be123c,stroke:#f43f5e,color:#fff
```

### AI Agent Roles
1. **Research Agent**: Scans educational databases (simulated search) for detailed topic explanations, LaTeX formulas, examples, and active educational hyperlinks.
2. **Summarizer Agent**: Builds structured markdown study notes, mnemonic memory tricks, key definitions, and rules.
3. **Quiz Generator Agent**: Generates MCQ, True/False, Fill-in-the-blank, short-answers, and mock coding questions. Implements **Adaptive Difficulty** based on previous attempts.
4. **Scheduler Agent**: Maps study blocks to the calendar. Weights subjects by priority/difficulty and **automatically rebalances study hours** to prioritize weak topics.
5. **Performance Analyzer**: Aggregates completions, quiz metrics, and streak counts into learning scores and action reports.
6. **Motivation Agent**: Decides study tip suggestions, recommended Pomodoro intervals, break reminders, and daily quotes.

---

## Database Schema (ER Diagram)

The database schema is implemented using SQLAlchemy with full cascading deletion relationships:

```mermaid
erDiagram
    USERS ||--o{ SUBJECTS : has
    USERS ||--o{ EXAMS : takes
    USERS ||--o{ PROGRESS : logs
    SUBJECTS ||--o{ TOPICS : contains
    TOPICS ||--o{ NOTES : includes
    TOPICS ||--o{ FLASHCARDS : schedules
    TOPICS ||--o{ QUIZZES : triggers
    EXAMS ||--o{ STUDY_PLANS : generates
    
    USERS {
        int id PK
        string name
        string email UK
        string password
        string provider
        datetime created_at
    }
    SUBJECTS {
        int id PK
        int user_id FK
        string name
        string difficulty
    }
    TOPICS {
        int id PK
        int subject_id FK
        string title
        string status
        string confidence
    }
    EXAMS {
        int id PK
        int user_id FK
        string name
        date exam_date
        string priority
        string difficulty
    }
    STUDY_PLANS {
        int id PK
        int exam_id FK
        text plan_json
        datetime generated_at
    }
    NOTES {
        int id PK
        int topic_id FK
        text content
    }
    FLASHCARDS {
        int id PK
        int topic_id FK
        text question
        text answer
        date review_date
        int interval
        float ease_factor
        int repetitions
    }
    QUIZZES {
        int id PK
        int topic_id FK
        text questions
        text answers
        float score
        string difficulty
    }
    PROGRESS {
        int id PK
        int user_id FK
        date date
        float study_hours
        float quiz_score
        float completion
        int active_streak
    }
```

---

## Features Implemented

*   **JWT Authorization**: Secure signup, login, cookie sessions, and developer mock Google login.
*   **Dynamic Study Scheduler**: Visual day-by-day timetable spreading sessions from today to exam date.
*   **Adaptive Testing**: Practice arena evaluating MCQ, text, or coding answers with immediate correction.
*   **Feedback Rebalance Loop**: Poor quiz marks (< 60%) lower topic confidence and trigger immediate calendar rebalance.
*   **Spaced Repetition (SM-2)**: Flip revision cards and rate your retention quality from 1 to 5 to dynamically recalculate review intervals.
*   **RAG PDF Intelligence**: Index PDF slide decks/textbooks into database chunks and query them directly for contextual tutoring answers.
*   **OCR Image Scan**: Scan handwriting/printed sheets to extract textual summaries and generate quizzes.
*   **Gamified Streaks**: Consistency metrics displaying active streak badges and achievements.

---

## Local Setup & Installation

### Option 1: Using Docker Compose (Recommended)

1. Ensure PostgreSQL is enabled and your Ollama service is running locally.
2. Build and run the services:
   ```bash
   docker-compose up --build
   ```
3. Open the browser:
   *   Streamlit App: `http://localhost:8501`
   *   Backend API (Swagger Docs): `http://localhost:8000/docs`

### Option 2: Manual Installation (Development)

#### Backend Setup
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend/` folder:
   ```env
   DATABASE_URL=postgresql+psycopg2://studyuser:studysecret@localhost:5432/studyplanner
   SECRET_KEY=yoursecretkeyhere
   DEFAULT_PROVIDER=ollama
   DEFAULT_MODEL=gpt-4.1-mini
   OLLAMA_BASE_URL=http://localhost:11434
   ```
5. Launch the FastAPI server:
   ```bash
   python main.py
   ```


## Testing

Run python unit and integration tests using pytest:
```bash
pytest backend/tests/
```
