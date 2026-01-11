from crewai import Task

class UniversityTasks:
    """Define tasks for all university agents"""
    
    @staticmethod
    def notice_task(agent, query: str):
        """Task for fetching notice information"""
        return Task(
            description=f"""
            Find official university notices and announcements about: {query}
            
            Use the hybrid search tool to:
            1. Search for relevant notices on official university websites
            2. Extract important details like dates, deadlines, and requirements
            3. Verify the information is current and official
            
            Provide a comprehensive answer in Bengali or English (whichever the query is in).
            Include all relevant dates and important details.
            
            Query: {query}
            """,
            expected_output="Clear, accurate information about the requested notice with all important details including dates and deadlines",
            agent=agent
        )
    
    @staticmethod
    def faculty_task(agent, query: str):
        """Task for fetching faculty information"""
        return Task(
            description=f"""
            Find information about university faculty members: {query}
            
            Use the hybrid search tool to:
            1. Search for faculty/teacher information on official university pages
            2. Extract names, designations, departments, and contact details
            3. Include office hours if available
            
            Provide organized, accurate information in the language of the query.
            
            Query: {query}
            """,
            expected_output="Detailed faculty information with names, departments, designations, and contact details",
            agent=agent
        )
    
    @staticmethod
    def library_task(agent, query: str):
        """Task for fetching library information"""
        return Task(
            description=f"""
            Find library-related information: {query}
            
            Use the hybrid search tool to:
            1. Search for library information on official university library pages
            2. Extract opening hours, services, rules, and facilities
            3. Include any special requirements or procedures
            
            Provide practical, actionable information in the language of the query.
            
            Query: {query}
            """,
            expected_output="Clear library information including timings, services, and any relevant rules or procedures",
            agent=agent
        )
    
    @staticmethod
    def about_task(agent, query: str):
        """Task for general university information"""
        return Task(
            description=f"""
            Find general information about the university: {query}
            
            Use the hybrid search tool to:
            1. Search for university history, mission, vision, or general information
            2. Extract facts about establishment, programs, facilities
            3. Provide comprehensive overview
            
            Give accurate, official information in the language of the query.
            
            Query: {query}
            """,
            expected_output="Comprehensive information about the university including relevant facts and details",
            agent=agent
        )
    
    @staticmethod
    def event_task(agent, query: str):
        """Task for university events and activities"""
        return Task(
            description=f"""
            Find information about university events and activities: {query}
            
            Use the hybrid search tool to:
            1. Search for upcoming events, seminars, workshops, or activities
            2. Extract dates, venues, registration details
            3. Include any participation requirements
            
            Provide timely, complete information in the language of the query.
            
            Query: {query}
            """,
            expected_output="Detailed event information including dates, venues, and how to participate",
            agent=agent
        )
    
    @staticmethod
    def department_task(agent, query: str):
        """Task for department-specific information"""
        return Task(
            description=f"""
            Find information about academic departments and programs: {query}
            
            Use the hybrid search tool to:
            1. Search for department information, programs, and courses
            2. Extract details about department structure, facilities, and activities
            3. Include contact information and location
            
            Provide accurate departmental information in the language of the query.
            
            Query: {query}
            """,
            expected_output="Comprehensive department information including programs, facilities, and contact details",
            agent=agent
        )
