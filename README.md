# CrewAI Job Search Assistant

This project creates a multi-agent job search and application assistant using CrewAI and a simple web UI.

## Features
- FastAPI backend with a job search API
- CrewAI-based orchestration for researching and ranking jobs
- Simple web UI to submit a role, location, experience, and resume summary
- OpenAI API key support for LLM-backed tasks

## Setup
1. Create a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
4. Start the app: `python run.py`
5. Open http://localhost:8000/ to use the UI.

## Testing
Run: `pytest -q`
