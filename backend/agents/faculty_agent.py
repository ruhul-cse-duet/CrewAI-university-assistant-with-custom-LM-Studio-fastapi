from crewai import Agent
from llm import get_llm
from tools.hybrid_search import university_hybrid_search

class FacultyAgent:
    @staticmethod
    def create():
        return Agent(
            role='Faculty & Department Information Specialist',
            goal='Provide detailed information about university faculty members, teachers, departments, and academic staff',
            backstory="""You are an expert at finding information about university faculty and departments.
            You can search for faculty names, designations, contact details, office hours, and specializations.
            You always provide accurate, verified information from official university sources.
            You can understand and respond in both Bengali and English.""",
            tools=[university_hybrid_search],
            llm=get_llm(),
            verbose=True,
            allow_delegation=False
        )
