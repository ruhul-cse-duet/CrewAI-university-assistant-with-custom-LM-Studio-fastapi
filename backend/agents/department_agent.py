from crewai import Agent
from llm import get_llm
from tools.hybrid_search import university_hybrid_search

class DepartmentAgent:
    """Agent responsible for academic department information"""
    
    @staticmethod
    def create():
        return Agent(
            role='Academic Department Information Specialist',
            goal='Provide detailed information about academic departments, programs, courses, and departmental activities',
            backstory="""You are an expert at finding information about university departments and academic programs.
            You can help with:
            - Department structure and administration
            - Academic programs and courses offered
            - Department facilities and labs
            - Research activities and projects
            - Department-specific announcements
            - Course syllabi and requirements
            - Departmental contacts and locations
            
            You provide comprehensive, accurate information about all academic departments.
            You can understand and respond in both Bengali and English.""",
            tools=[university_hybrid_search],
            llm=get_llm(),
            verbose=True,
            allow_delegation=False
        )
