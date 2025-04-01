import datetime
from typing import Optional

from app.api.canvas_client import CanvasClient
from app.services.openai_service import OpenAIService
from app.logger import logger
from app.utils.loading_utils import LoadingAnimation

class CanvasAI:
    '''
    A versatile agent that can perform a wide range of tasks using Canvas API based on user input.
    '''
    
    name: str = "canvasai"
    description: str = (
        "A versatile agent that can solve academic questions using multiple tools"
    )
    
    def __init__(self):
        # Initialize APIs and services
        self.canvas_client = CanvasClient()
        self.openai_service = OpenAIService()
        
        # Conversation history for context
        self.conversation_history = []
        self.max_history_length = 10
    
    def authenticate_user(self, user_token: Optional[str] = None) -> bool:
        """Authenticate user with Canvas API"""
        logger.info("Authenticating user with Canvas API...")
        with LoadingAnimation("Authenticating", "spinner"):
            result = self.canvas_client.authenticate_user(user_token)
        
        if result:
            logger.info("Authentication successful")
        else:
            logger.error("Authentication failed")
        return result
    
    def update_conversation_history(self, user_query: str, bot_response: str):
        """Update conversation history with the latest exchange"""
        self.conversation_history.append({
            "user": user_query,
            "assistant": bot_response,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Trim history if it exceeds max length
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def _prepare_context(self, query: str) -> str:
        """Prepare context for OpenAI by formatting conversation history"""
        context = "Previous conversation:\n"
        
        for exchange in self.conversation_history[-3:]:  # Last 3 exchanges
            context += f"User: {exchange['user']}\n"
            context += f"Assistant: {exchange['assistant']}\n"
        
        context += f"\nCurrent query: {query}\n"
        return context
    
    def _extract_course_id(self, course_name: str) -> Optional[int]:
        """Extract course ID from course name or partial name"""
        courses = self.canvas_client.load_active_courses()
        
        # Try exact match first
        for course in courses:
            if course["name"].lower() == course_name.lower():
                return course["id"]
        
        # Try partial match
        for course in courses:
            if course_name.lower() in course["name"].lower():
                return course["id"]
        
        return None
    
    async def run(self, query: str):
        """Run the agent with the given query (async interface for potential future use)"""
        return self.process_query(query)
    
    def process_query(self, query: str) -> str:
        """
        Process a natural language query from the student
        Uses OpenAI to understand the query and formulate a response
        """
        try:
            # First, use OpenAI to classify the query and extract key information
            logger.info("Classifying query...")
            with LoadingAnimation("Analyzing your question", "spinner"):
                classification = self.openai_service.classify_query(query)
            
            # Extract relevant information based on classification
            query_type = classification.get("query_type", "unknown")
            course_name = classification.get("course")
            logger.info(f"Query classified as: {query_type}, Course: {course_name or 'None'}")
            
            # Get data based on query type
            data = {}
            
            # Always load courses as base data
            logger.info("Loading course data...")
            with LoadingAnimation("Fetching course information", "spinner"):
                data["courses"] = self.canvas_client.load_active_courses()
            
            # Get course-specific information if a course was mentioned
            if course_name:
                logger.info(f"Looking up course: {course_name}")
                with LoadingAnimation(f"Finding course '{course_name}'", "spinner"):
                    course_id = self._extract_course_id(course_name)
                
                if course_id:
                    logger.info(f"Found course ID: {course_id}")
                    
                    if query_type in ["assignments", "deadlines"]:
                        logger.info(f"Fetching assignments for course {course_id}")
                        with LoadingAnimation("Retrieving assignments", "spinner"):
                            data["assignments"] = self.canvas_client.get_course_assignments(course_id)
                    
                    if query_type in ["grades"]:
                        logger.info(f"Fetching grades for course {course_id}")
                        with LoadingAnimation("Retrieving grades", "spinner"):
                            data["grades"] = self.canvas_client.get_course_grades(course_id)
                    
                    if query_type in ["course_materials", "modules"]:
                        logger.info(f"Fetching modules and files for course {course_id}")
                        with LoadingAnimation("Retrieving course materials", "spinner"):
                            data["modules"] = self.canvas_client.get_course_modules(course_id)
                            data["files"] = self.canvas_client.get_course_files(course_id)
                    
                    if query_type in ["announcements"]:
                        logger.info(f"Fetching announcements for course {course_id}")
                        with LoadingAnimation("Retrieving announcements", "spinner"):
                            data["announcements"] = self.canvas_client.get_course_announcements(course_id)
                    
                    # Get detailed course info
                    logger.info(f"Fetching detailed course information for {course_id}")
                    with LoadingAnimation("Getting course details", "spinner"):
                        data["course_details"] = self.canvas_client.get_course_details(course_id)
                        data["course_id"] = course_id
                else:
                    logger.warning(f"Could not find course matching '{course_name}'")
            
            # Get global information for certain query types
            if query_type in ["deadlines", "upcoming"] or not course_name:
                logger.info("Fetching upcoming deadlines across all courses")
                with LoadingAnimation("Checking upcoming deadlines", "spinner"):
                    data["upcoming_deadlines"] = self.canvas_client.get_upcoming_deadlines()
            
            # Now, use OpenAI to generate a response based on the fetched data
            context = self._prepare_context(query)
            
            # Generate response
            logger.info("Generating response based on collected data")
            with LoadingAnimation("Formulating response", "spinner"):
                bot_response = self.openai_service.generate_response(context, data, query)
            
            # Update conversation history
            self.update_conversation_history(query, bot_response)
            logger.info("Response generated successfully")
            
            return bot_response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your query. Please try again or rephrase your question. Error details: {str(e)}"
    
    def load_active_courses(self):
        """Convenience method to directly access canvas client"""
        logger.info("Loading active courses")
        with LoadingAnimation("Loading active courses", "spinner"):
            return self.canvas_client.load_active_courses()
