import datetime
from typing import Optional

def format_iso_date(date_str: str) -> str:
    """Format ISO date string to human-readable format"""
    if not date_str:
        return "No date specified"
    
    try:
        date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date.strftime("%A, %B %d, %Y at %I:%M %p")
    except:
        return date_str

def parse_canvas_date(due_date_str: str) -> Optional[datetime.datetime]:
    """Parse Canvas date format to datetime object"""
    if not due_date_str:
        return None
        
    try:
        # Handle the 'Z' timezone designator
        if due_date_str.endswith('Z'):
            due_date = datetime.datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        else:
            # Add UTC timezone if missing
            due_date = datetime.datetime.fromisoformat(due_date_str)
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=datetime.timezone.utc)
        return due_date
    except ValueError:
        # Fall back to a simpler parsing method if ISO format fails
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ")
            due_date = due_date.replace(tzinfo=datetime.timezone.utc)
            return due_date
        except ValueError:
            return None
