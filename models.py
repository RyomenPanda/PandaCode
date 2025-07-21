from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AIResponse:
    """Represents response from AI service"""
    success: bool
    content: str
    error: Optional[str] = None

@dataclass
class GitStatus:
    """Represents Git repository status"""
    branch: str
    modified_files: List[str]
    staged_files: List[str]
    untracked_files: List[str]
