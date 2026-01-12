from crewai import Crew, Process
from agents import NoticeAgent, FacultyAgent, LibraryAgent, AboutAgent, EventAgent, DepartmentAgent
from tasks import UniversityTasks
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class UniversityCrew:
    """Orchestrate agents to answer university-related queries"""
    
    def __init__(self):
        # Initialize all agents
        self.notice_agent = NoticeAgent.create()
        self.faculty_agent = FacultyAgent.create()
        self.library_agent = LibraryAgent.create()
        self.about_agent = AboutAgent.create()
        self.event_agent = EventAgent.create()
        self.department_agent = DepartmentAgent.create()
        self.tasks = UniversityTasks()
        
        logger.info("UniversityCrew initialized with all agents")
    
    def identify_query_type(self, query: str) -> str:
        """Identify which agent should handle the query"""
        query_lower = query.lower()
        
        # Define keywords for each agent type
        agent_keywords = {
            'notice': [
                'notice', 'নোটিশ', 'announcement', 'ঘোষণা', 
                'deadline', 'শেষ তারিখ', 'exam', 'পরীক্ষা', 
                'form', 'ফর্ম', 'schedule', 'সময়সূচী', 
                'date', 'তারিখ', 'circular', 'সার্কুলার'
            ],
            'faculty': [
                'teacher', 'শিক্ষক', 'faculty', 'অনুষদ', 
                'professor', 'প্রফেসর', 'lecturer', 'শিক্ষিকা',
                'sir', 'madam', 'contact', 'যোগাযোগ', 'mam',
                'email', 'phone', 'ইমেইল', 'ফোন'
            ],
            'library': [
                'library', 'লাইব্রেরি', 'বই', 'book', 
                'timing', 'সময়', 'বন্ধ', 'খোলা', 
                'open', 'close', 'reading room', 'পড়ার ঘর'
            ],
            'department': [
                'department', 'বিভাগ', 'dept', 'program', 'প্রোগ্রাম',
                'course', 'কোর্স', 'syllabus', 'সিলেবাস', 
                'cse', 'eee', 'civil', 'mechanical', 'textile'
            ],
            'event': [
                'event', 'ইভেন্ট', 'seminar', 'সেমিনার',
                'workshop', 'কর্মশালা', 'cultural', 'সাংস্কৃতিক',
                'sports', 'খেলাধুলা', 'program', 'অনুষ্ঠান',
                'competition', 'প্রতিযোগিতা'
            ],
            'about': [
                'about', 'সম্পর্কে', 'history', 'ইতিহাস',
                'mission', 'লক্ষ্য', 'vision', 'ভিশন',
                'established', 'প্রতিষ্ঠা', 'founded', 'campus', 'ক্যাম্পাস'
            ]
        }
        
        # Count keyword matches for each agent
        scores = {agent_type: 0 for agent_type in agent_keywords.keys()}
        
        for agent_type, keywords in agent_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[agent_type] += 1
        
        # Return agent type with highest score
        if max(scores.values()) > 0:
            selected_agent = max(scores, key=scores.get)
            logger.info(f"Selected agent: {selected_agent} (score: {scores[selected_agent]})")
            return selected_agent
        
        # Default to notice agent if no matches
        logger.info("No keyword matches, defaulting to notice agent")
        return 'notice'
    
    def process_query(self, query: str) -> Dict[str, str]:
        """Process user query and return response"""
        
        try:
            # Identify query type
            query_type = self.identify_query_type(query)
            logger.info(f"Processing {query_type} query: {query[:50]}...")
            
            # Select appropriate agent and task
            if query_type == 'notice':
                agent = self.notice_agent
                task = self.tasks.notice_task(agent, query)
            elif query_type == 'faculty':
                agent = self.faculty_agent
                task = self.tasks.faculty_task(agent, query)
            elif query_type == 'library':
                agent = self.library_agent
                task = self.tasks.library_task(agent, query)
            elif query_type == 'department':
                agent = self.department_agent
                task = self.tasks.department_task(agent, query)
            elif query_type == 'event':
                agent = self.event_agent
                task = self.tasks.event_task(agent, query)
            else:  # about
                agent = self.about_agent
                task = self.tasks.about_task(agent, query)
            
            # Create crew with single agent and task
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute and get result
            logger.info("Executing crew kickoff...")
            result = crew.kickoff()
            
            logger.info("Query processed successfully")
            return {
                'query': query,
                'query_type': query_type,
                'response': str(result),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                'query': query,
                'query_type': 'error',
                'response': f'Error processing query: {str(e)}',
                'status': 'error'
            }
