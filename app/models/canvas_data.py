from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Course:
    id: int
    name: str
    course_code: str
    term: Optional[Dict] = None
    syllabus_body: Optional[str] = None
    teachers: Optional[List[Dict]] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            course_code=data.get("course_code", ""),
            term=data.get("term"),
            syllabus_body=data.get("syllabus_body"),
            teachers=data.get("teachers")
        )

@dataclass
class Assignment:
    id: int
    name: str
    description: str
    due_at: Optional[str]
    points_possible: float
    submission: Optional[Dict] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Assignment':
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            due_at=data.get("due_at"),
            points_possible=data.get("points_possible", 0.0),
            submission=data.get("submission")
        )

@dataclass
class Module:
    id: int
    name: str
    position: int
    items: List[Dict]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Module':
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            position=data.get("position", 0),
            items=data.get("items", [])
        )

@dataclass
class File:
    id: int
    filename: str
    display_name: str
    url: str
    size: int
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'File':
        return cls(
            id=data.get("id"),
            filename=data.get("filename", ""),
            display_name=data.get("display_name", ""),
            url=data.get("url", ""),
            size=data.get("size", 0)
        )

@dataclass
class Announcement:
    id: int
    title: str
    message: str
    posted_at: str
    author: Dict
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Announcement':
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            message=data.get("message", ""),
            posted_at=data.get("posted_at", ""),
            author=data.get("author", {})
        )

@dataclass
class Conversation:
    user: str
    assistant: str
    timestamp: str
