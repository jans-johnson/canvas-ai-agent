import json
from openai import OpenAI
from typing import Dict, List, Optional

from app.logger import logger
from app.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from app.prompt.canvasai import CLASSIFICATION_PROMPT, RESPONSE_GENERATION_PROMPT, GENERATION_ERROR_RESPONSE

class OpenAIService:
    """Service for interacting with OpenAI APIs"""

    def __init__(self):
        self.openai = OpenAI(api_key=OPENAI_API_KEY,base_url=OPENAI_BASE_URL)
    
    def classify_query(self, query: str, courses: Optional[List[Dict]] = None) -> Dict:
        """
        Classify a user query to determine what information is needed
        and match any mentioned course to the available courses
        
        Args:
            query: The user's query
            courses: Optional list of course objects to match against
        """
        # Format available courses for the prompt if provided
        courses_text = ""
        if courses:
            courses_text = "Available courses:\n" + "\n".join([
                f"ID: {course.get('id', 'Unknown')}, Name: {course.get('name', 'Unknown')}" 
                for course in courses
            ])
        
        prompt = CLASSIFICATION_PROMPT.format(
            query=query,
            courses_text=courses_text
        )
        logger.debug("Sending classification request to OpenAI")
        
        try:
            # Make a request to OpenAI for query classification
            response = self.openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,  # Lower temperature for more predictable formatting
                max_tokens=500,
                response_format={"type": "json_object"}  # Force JSON response format
            )
            
            response_content = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI JSON response: {response_content}")
            
            try:
                # Parse the classification result
                classification = json.loads(response_content)
                logger.info(f"Query classified as: {classification.get('query_type')}")
                
                # Log course matching result if available
                if classification.get("course_id"):
                    logger.info(f"Course matched: {classification.get('course')} (ID: {classification.get('course_id')}, Confidence: {classification.get('course_match_confidence')})")
                
                return classification
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                logger.error(f"Failed to parse OpenAI response as JSON: {e}\nResponse: {response_content}")
                return {
                    "query_type": "unknown",
                    "course": None,
                    "course_id": None,
                    "course_match_confidence": None,
                    "time_frame": None,
                    "specific_item": None,
                    "api_calls": ["load_active_courses"]
                }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "query_type": "unknown",
                "course": None,
                "course_id": None,
                "course_match_confidence": None,
                "time_frame": None,
                "specific_item": None,
                "api_calls": ["load_active_courses"]
            }
    
    def generate_response(self, context: str, data: Dict, query: str) -> str:
        """
        Generate a response based on the query, context, and data
        """
        # Convert data to a JSON string for the prompt
        data_str = json.dumps(data, indent=2)
        
        prompt = RESPONSE_GENERATION_PROMPT.format(
            context=context,
            data_str=data_str
        )
        
        logger.debug("Sending response generation request to OpenAI")
        try:
            # Make a request to OpenAI for response generation
            response = self.openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Get the generated response
            logger.info("Response generated successfully")
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error during response generation: {e}")
            return GENERATION_ERROR_RESPONSE
