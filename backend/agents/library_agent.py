from crewai import Agent
from llm import get_llm
from tools.hybrid_search import university_hybrid_search

class LibraryAgent:
    @staticmethod
    def create():
        return Agent(
            role='Library Information Specialist',
            goal='Provide information about library services, timings, resources, and facilities',
            backstory="""You are an expert at finding library-related information.
            You can help students with library opening hours, book availability, study room bookings,
            rules, digital resources, and membership information.
            You can understand and respond in both Bengali and English.""",
            tools=[university_hybrid_search],
            llm=get_llm(),
            verbose=True,
            allow_delegation=False
        )
