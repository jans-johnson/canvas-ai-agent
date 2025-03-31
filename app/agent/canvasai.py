import os
import json
import openai
from typing import Dict, List, Optional, Any, Tuple
import requests
import time
import datetime
from dotenv import load_dotenv


load_dotenv()

class canvasAI():
    '''
    A versatile agent that can perform a wide range of tasks using Canvas API based on user input.
    '''
    
    name: str = "canvasai"
    description: str = (
        "A versatile agent that can solve academic quesitons using multiple tools"
    )
    def __init__(self):
        # Load API keys and URLs from environment variables
        self.canvas_api_key = os.getenv("CANVAS_API_KEY")
        self.canvas_url = os.getenv("CANVAS_API_URL", "https://canvas.instructure.com/api/v1")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client
        openai.api_key = self.openai_api_key
        
        # Initialize cache
        self.cache = {
            "courses": {},
            "assignments": {},
            "announcements": {},
            "grades": {},
            "modules": {},
            "files": {},
            "user_info": None,
            "last_updated": {}
        }
        
        # Cache expiration time (in seconds)
        self.cache_expiration = {
            "courses": 3600,  # 1 hour
            "assignments": 1800,  # 30 minutes
            "announcements": 1800,  # 30 minutes
            "grades": 1800,  # 30 minutes
            "modules": 3600,  # 1 hour
            "files": 3600,  # 1 hour
            "user_info": 86400  # 24 hours
        }
        
        # Conversation history for context
        self.conversation_history = []
        self.max_history_length = 10
        
    def authenticate_user(self, user_token: Optional[str] = None) -> bool:
        """
        Authenticate user with Canvas API
        Returns True if authentication is successful, False otherwise
        """
        # If token is provided, use it instead of the default one
        token = user_token if user_token else self.canvas_api_key
        
        if not token:
            return False
        
        # Try to fetch user info to verify token
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{self.canvas_url}/users/self", headers=headers)
            if response.status_code == 200:
                self.cache["user_info"] = response.json()
                return True
            return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def _check_cache(self, cache_type: str, identifier: Optional[str] = None) -> Tuple[bool, Any]:
        """Check if cache is valid and return cached data if it is"""
        current_time = time.time()
        
        # If cache type doesn't exist or hasn't been updated yet
        if cache_type not in self.cache or cache_type not in self.cache["last_updated"]:
            return False, None
        
        # If specific identifier is requested
        if identifier:
            if identifier not in self.cache[cache_type]:
                return False, None
            
            last_updated = self.cache["last_updated"].get(f"{cache_type}_{identifier}")
            if not last_updated or (current_time - last_updated) > self.cache_expiration[cache_type]:
                return False, None
            
            return True, self.cache[cache_type][identifier]
        else:
            # Check overall cache validity
            last_updated = self.cache["last_updated"].get(cache_type)
            if not last_updated or (current_time - last_updated) > self.cache_expiration[cache_type]:
                return False, None
            
            return True, self.cache[cache_type]
    
    def _update_cache(self, cache_type: str, data: Any, identifier: Optional[str] = None):
        """Update cache with new data"""
        current_time = time.time()
        
        if identifier:
            if cache_type not in self.cache:
                self.cache[cache_type] = {}
            self.cache[cache_type][identifier] = data
            self.cache["last_updated"][f"{cache_type}_{identifier}"] = current_time
        else:
            self.cache[cache_type] = data
            self.cache["last_updated"][cache_type] = current_time
    
    def load_active_courses(self) -> List[Dict]:
        """Fetch and store active courses for the authenticated user"""
        # Check cache first
        is_cached, cached_courses = self._check_cache("courses")
        if is_cached:
            return cached_courses
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses",
                headers=headers,
                params={"enrollment_state": "active", "include": ["term"]}
            )
            
            if response.status_code == 200:
                courses = response.json()
                active_courses = [course for course in courses if not course.get("access_restricted_by_date")]
                
                # Update cache
                self._update_cache("courses", active_courses)
                
                # Pre-fetch assignments for each course to improve performance
                for course in active_courses:
                    self.get_course_assignments(course["id"])
                
                return active_courses
            else:
                print(f"Error fetching courses: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Error loading courses: {e}")
            return []
    
    def get_course_details(self, course_id: int) -> Dict:
        """Get detailed information about a specific course"""
        # Check cache first
        is_cached, cached_course = self._check_cache("courses", str(course_id))
        if is_cached:
            return cached_course
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses/{course_id}",
                headers=headers,
                params={"include": ["syllabus_body", "term", "teachers"]}
            )
            
            if response.status_code == 200:
                course_details = response.json()
                # Update cache
                self._update_cache("courses", course_details, str(course_id))
                return course_details
            else:
                print(f"Error fetching course details: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting course details: {e}")
            return {}
    
    def get_course_assignments(self, course_id: int) -> List[Dict]:
        """Get assignments for a specific course"""
        # Check cache first
        is_cached, cached_assignments = self._check_cache("assignments", str(course_id))
        if is_cached:
            return cached_assignments
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses/{course_id}/assignments",
                headers=headers,
                params={"include": ["submission"]}
            )
            
            if response.status_code == 200:
                assignments = response.json()
                # Update cache
                self._update_cache("assignments", assignments, str(course_id))
                return assignments
            else:
                print(f"Error fetching assignments: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Error getting assignments: {e}")
            return []
    
    def get_upcoming_deadlines(self) -> List[Dict]:
        """Get upcoming assignment deadlines across all active courses"""
        try:
            # Get all active courses
            courses = self.load_active_courses()
            upcoming_deadlines = []
            
            # Get current date with timezone awareness
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for course in courses:
                course_id = course["id"]
                assignments = self.get_course_assignments(course_id)
                
                for assignment in assignments:
                    # Skip if no due date
                    if not assignment.get("due_at"):
                        continue
                    
                    # Parse the date with timezone awareness
                    due_date_str = assignment["due_at"]
                    # Make sure we handle the 'Z' timezone designator properly
                    if due_date_str.endswith('Z'):
                        due_date = datetime.datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    else:
                        # Add UTC timezone if missing
                        try:
                            due_date = datetime.datetime.fromisoformat(due_date_str)
                            if due_date.tzinfo is None:
                                due_date = due_date.replace(tzinfo=datetime.timezone.utc)
                        except ValueError:
                            # Fall back to a simpler parsing method if ISO format fails
                            try:
                                due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ")
                                due_date = due_date.replace(tzinfo=datetime.timezone.utc)
                            except ValueError:
                                # Skip this assignment if we can't parse the date
                                continue
                    
                    # Check if assignment is upcoming (due in the future)
                    if due_date > now:
                        upcoming_deadlines.append({
                            "course_name": course["name"],
                            "course_id": course_id,
                            "assignment_name": assignment["name"],
                            "assignment_id": assignment["id"],
                            "due_date": assignment["due_at"],
                            "points_possible": assignment["points_possible"],
                            "submitted": assignment.get("submission", {}).get("submitted_at") is not None
                        })
            
            # Sort by due date
            upcoming_deadlines.sort(key=lambda x: x["due_date"])
            return upcoming_deadlines
        except Exception as e:
            print(f"Error getting upcoming deadlines: {e}")
            return []
    
    def get_course_grades(self, course_id: int) -> Dict:
        """Get grades for a specific course"""
        # Check cache first
        is_cached, cached_grades = self._check_cache("grades", str(course_id))
        if is_cached:
            return cached_grades
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses/{course_id}/assignments",
                headers=headers,
                params={"include": ["submission"]}
            )
            
            if response.status_code == 200:
                assignments = response.json()
                
                # Also get the overall course grade
                course_response = requests.get(
                    f"{self.canvas_url}/courses/{course_id}",
                    headers=headers,
                    params={"include": ["total_scores"]}
                )
                
                course_info = course_response.json() if course_response.status_code == 200 else {}
                
                grades_info = {
                    "overall": course_info.get("enrollments", [{}])[0].get("computed_current_score", None),
                    "assignments": []
                }
                
                for assignment in assignments:
                    submission = assignment.get("submission", {})
                    grades_info["assignments"].append({
                        "assignment_name": assignment["name"],
                        "assignment_id": assignment["id"],
                        "points_possible": assignment["points_possible"],
                        "score": submission.get("score"),
                        "submitted": submission.get("submitted_at") is not None,
                        "graded": submission.get("grade") is not None
                    })
                
                # Update cache
                self._update_cache("grades", grades_info, str(course_id))
                return grades_info
            else:
                print(f"Error fetching grades: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting grades: {e}")
            return {}
    
    def get_course_modules(self, course_id: int) -> List[Dict]:
        """Get modules and items for a specific course"""
        # Check cache first
        is_cached, cached_modules = self._check_cache("modules", str(course_id))
        if is_cached:
            return cached_modules
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses/{course_id}/modules",
                headers=headers,
                params={"include": ["items"]}
            )
            
            if response.status_code == 200:
                modules = response.json()
                
                # For each module, fetch its items
                for module in modules:
                    items_response = requests.get(
                        f"{self.canvas_url}/courses/{course_id}/modules/{module['id']}/items",
                        headers=headers
                    )
                    
                    if items_response.status_code == 200:
                        module["items"] = items_response.json()
                    else:
                        module["items"] = []
                
                # Update cache
                self._update_cache("modules", modules, str(course_id))
                return modules
            else:
                print(f"Error fetching modules: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Error getting modules: {e}")
            return []
    
    def get_course_files(self, course_id: int) -> List[Dict]:
        """Get files for a specific course"""
        # Check cache first
        is_cached, cached_files = self._check_cache("files", str(course_id))
        if is_cached:
            return cached_files
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses/{course_id}/files",
                headers=headers
            )
            
            if response.status_code == 200:
                files = response.json()
                # Update cache
                self._update_cache("files", files, str(course_id))
                return files
            else:
                print(f"Error fetching files: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Error getting files: {e}")
            return []
    
    def get_course_announcements(self, course_id: int) -> List[Dict]:
        """Get announcements for a specific course"""
        # Check cache first
        is_cached, cached_announcements = self._check_cache("announcements", str(course_id))
        if is_cached:
            return cached_announcements
        
        # Fetch from API if not cached
        headers = {"Authorization": f"Bearer {self.canvas_api_key}"}
        try:
            response = requests.get(
                f"{self.canvas_url}/courses/{course_id}/discussion_topics",
                headers=headers,
                params={"only_announcements": True}
            )
            
            if response.status_code == 200:
                announcements = response.json()
                # Update cache
                self._update_cache("announcements", announcements, str(course_id))
                return announcements
            else:
                print(f"Error fetching announcements: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Error getting announcements: {e}")
            return []

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
        courses = self.load_active_courses()
        
        # Try exact match first
        for course in courses:
            if course["name"].lower() == course_name.lower():
                return course["id"]
        
        # Try partial match
        for course in courses:
            if course_name.lower() in course["name"].lower():
                return course["id"]
        
        return None
    
    def _format_date(self, date_str: str) -> str:
        """Format ISO date string to human-readable format"""
        if not date_str:
            return "No date specified"
        
        try:
            date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date.strftime("%A, %B %d, %Y at %I:%M %p")
        except:
            return date_str
    
    def process_query(self, query: str) -> str:
        """
        Process a natural language query from the student
        Uses OpenAI to understand the query and formulate a response
        """
        try:
            # First, use OpenAI to classify the query and extract key information
            prompt = f"""
            You are an AI assistant for a Canvas LMS student chatbot. 
            Analyze the following student query and determine what information 
            is needed from the Canvas API:
            
            "{query}"
            
            Identify:
            1. The query type (e.g., assignments, deadlines, grades, course materials, general guidance)
            2. Specific course mentioned (if any)
            3. Time frame mentioned (if any)
            4. Specific assignment/material mentioned (if any)
            5. What API calls would be needed to answer this query
            
            Format your response as a JSON object with these keys.
            """
            
            # Make a request to OpenAI for query classification
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            try:
                # Parse the classification result
                classification = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                classification = {
                    "query_type": "unknown",
                    "course": None,
                    "time_frame": None,
                    "specific_item": None,
                    "api_calls": ["load_active_courses"]
                }
            
            # Extract relevant information based on classification
            query_type = classification.get("query_type", "unknown")
            course_name = classification.get("course")
            
            # Get data based on query type
            data = {}
            
            # Always load courses as base data
            data["courses"] = self.load_active_courses()
            
            # Get course-specific information if a course was mentioned
            if course_name:
                course_id = self._extract_course_id(course_name)
                
                if course_id:
                    if query_type in ["assignments", "deadlines"]:
                        data["assignments"] = self.get_course_assignments(course_id)
                    
                    if query_type in ["grades"]:
                        data["grades"] = self.get_course_grades(course_id)
                    
                    if query_type in ["course_materials", "modules"]:
                        data["modules"] = self.get_course_modules(course_id)
                        data["files"] = self.get_course_files(course_id)
                    
                    if query_type in ["announcements"]:
                        data["announcements"] = self.get_course_announcements(course_id)
                    
                    # Get detailed course info
                    data["course_details"] = self.get_course_details(course_id)
                    data["course_id"] = course_id
            
            # Get global information for certain query types
            if query_type in ["deadlines", "upcoming"] or not course_name:
                data["upcoming_deadlines"] = self.get_upcoming_deadlines()
            
            # Now, use OpenAI to generate a response based on the fetched data
            context = self._prepare_context(query)
            
            # Convert data to a JSON string for the prompt
            data_str = json.dumps(data, indent=2)
            
            prompt = f"""
            You are an AI assistant for a Canvas LMS student chatbot. 
            Use the following data from the Canvas API to answer the student's query.
            
            CONTEXT:
            {context}
            
            API DATA:
            {data_str}
            
            Generate a helpful, concise response that directly answers the student's question.
            Include specific details from the API data when relevant.
            Format dates in a human-readable way.
            If you cannot answer based on the available data, suggest what information might be needed.
            """
            
            # Make a request to OpenAI for response generation
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Get the generated response
            bot_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.update_conversation_history(query, bot_response)
            
            return bot_response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your query. Please try again or rephrase your question. Error details: {str(e)}"
