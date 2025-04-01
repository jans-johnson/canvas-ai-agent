import json
import openai
from typing import Dict, Optional

from app.logger import logger
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.prompt.canvasai import CLASSIFICATION_PROMPT, RESPONSE_GENERATION_PROMPT, GENERATION_ERROR_RESPONSE
from app.utils.loading_utils import timed_action

class OpenAIService:
    """Service for interacting with OpenAI APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        openai.api_key = self.api_key
    
    def classify_query(self, query: str) -> Dict:
        """
        Classify a user query to determine what information is needed
        """
        prompt = CLASSIFICATION_PROMPT.format(query=query)
        logger.debug("Sending classification request to OpenAI")
        
        try:
            # Make a request to OpenAI for query classification
            response = openai.chat.completions.create(
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
                return classification
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                logger.error(f"Failed to parse OpenAI response as JSON: {e}\nResponse: {response_content}")
                return {
                    "query_type": "unknown",
                    "course": None,
                    "time_frame": None,
                    "specific_item": None,
                    "api_calls": ["load_active_courses"]
                }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "query_type": "unknown",
                "course": None,
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
            response = openai.chat.completions.create(
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
