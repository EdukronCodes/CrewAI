import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from crewai import Agent, Task, Crew
    from crewai.tools import BaseTool
except Exception:  # pragma: no cover
    Agent = Task = Crew = None
    BaseTool = object

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

class MockJobTool(BaseTool):
    name = "mock_job_search"
    description = "Searches a static list of jobs for demo purposes"

    def _run(self, query: str) -> str:
        jobs = [
            {
                "title": "Senior Python Engineer",
                "company": "Acme Labs",
                "location": "Remote",
                "match_score": 0.94,
                "why_match": "Strong Python and FastAPI experience"
            },
            {
                "title": "Backend Software Engineer",
                "company": "Northwind AI",
                "location": "New York, NY",
                "match_score": 0.88,
                "why_match": "Relevant API and cloud work"
            },
            {
                "title": "Staff Platform Engineer",
                "company": "Helio Systems",
                "location": "Remote",
                "match_score": 0.82,
                "why_match": "Experience with distributed systems"
            },
        ]
        return str(jobs)


def _fallback_matches(role: str, location: str) -> Dict[str, object]:
    return {
        "summary": f"Demo search for {role} in {location} using a local assistant profile.",
        "matches": [
            {
                "title": "Senior Python Engineer",
                "company": "Acme Labs",
                "location": location,
                "match_score": 0.94,
                "why_match": "Strong Python and FastAPI experience"
            },
            {
                "title": "Backend Software Engineer",
                "company": "Northwind AI",
                "location": "New York, NY",
                "match_score": 0.88,
                "why_match": "Relevant API and cloud work"
            },
        ],
    }


def generate_application_draft(role: str, company: str, job_title: str, resume_text: str) -> Dict[str, object]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured")

    try:
        prompt = (
            f"Write a concise cover letter for a {role} applying to {job_title} at {company}. "
            f"Mention this background: {resume_text or 'general software engineering experience'}."
        )
        content = _call_openai(prompt)
        payload = json.loads(content)
        if isinstance(payload, dict) and "cover_letter" in payload and "next_steps" in payload:
            return payload
    except Exception:
        pass

    return {
        "cover_letter": (
            f"Dear Hiring Team at {company},\n\n"
            f"I am excited to apply for the {job_title} position as a {role}. "
            f"My background in software engineering aligns well with this opportunity, and I would welcome the chance to discuss how I can contribute."
        ),
        "next_steps": ["Prepare your resume", "Submit the application", "Follow up in a week"],
    }


def _call_openai(prompt: str) -> str:
    if OpenAI is None:
        raise RuntimeError("openai package is not available")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful recruitment copilot that returns strict JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "{}"


def run_job_search(role: str, location: str, experience: str, resume_text: str, apply_context: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured")

    if Agent is not None:
        researcher = Agent(
            role="Researcher",
            goal="Find the best jobs for the user",
            backstory="You scan job postings and identify strong matches.",
            verbose=False,
            allow_delegation=False,
        )
        matcher = Agent(
            role="Matcher",
            goal="Rank the best opportunities and explain fit",
            backstory="You compare the candidate profile with roles and score the fit.",
            verbose=False,
            allow_delegation=False,
        )

        task1 = Task(
            description=(
                f"Search for {role} roles in {location}. Use the candidate background: {resume_text or 'general software engineering experience'}"
            ),
            agent=researcher,
            expected_output="A JSON array of matching jobs",
        )
        task2 = Task(
            description=(
                f"Review the matches and create a concise summary with the strongest opportunities for an {experience} level candidate."
            ),
            agent=matcher,
            expected_output="A summary string and ranked jobs",
        )

        crew = Crew(agents=[researcher, matcher], tasks=[task1, task2])
        crew.kickoff()

    try:
        prompt = (
            f"Return JSON with keys summary and matches for a {experience}-level {role} candidate in {location}. "
            f"Use resume background: {resume_text or 'general software engineering experience'}. "
            f"Generate 2 concise matches with title, company, location, match_score, and why_match."
        )
        payload = _call_openai(prompt)
        parsed = json.loads(payload)
        if isinstance(parsed, dict) and "summary" in parsed and "matches" in parsed:
            return parsed
    except Exception:
        pass

    return _fallback_matches(role, location)
