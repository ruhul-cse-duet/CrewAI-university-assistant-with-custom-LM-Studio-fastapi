from crewai import Agent
from llm import get_llm
from tools.hybrid_search import university_hybrid_search

class AboutAgent:
    """Agent responsible for general university information"""
    
    @staticmethod
    def create():
        return Agent(
            role='University Information Officer',
            goal='Provide comprehensive information about the university, its history, mission, vision, and general information',
            backstory="""You are an official university information officer with deep knowledge about:
            - University history and establishment
            - Mission and vision statements
            - Academic programs and faculties
            - Campus facilities and infrastructure
            - Admission process and requirements
            - University achievements and rankings
            - Contact information and locations
            
            You provide official, accurate information from university sources.
            You can understand and respond in both Bengali and English.""",
            tools=[university_hybrid_search],
            llm=get_llm(),
            verbose=True,
            allow_delegation=False
        )
