from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Structured finding within the code
class ReviewFinding(BaseModel):
    file_path: str = Field(..., description="The full path of the file where the issue was found")
    line_start: int = Field(..., description="The starting line number of the issue")
    line_end: int = Field(..., description="The ending line number of the issue")
    
    # UPDATE: Changed from strict Literal[...] to str
    # This accepts ANY word the AI chooses (CRITICAL, MAJOR, HIGH, etc.)
    severity: str = Field(..., description="How urgent is this? (e.g., CRITICAL, HIGH, MEDIUM, LOW)")
    
    # UPDATE: Changed from strict Literal[...] to str
    category: str = Field(..., description="The type of issue (e.g., SECURITY, BUG, STYLE)")
    
    suggestion: str = Field(..., description="Concise advice on how to fix it")
    code_snippet: Optional[str] = Field(None, description="The problematic code (for context)")

# 2. The full AI response object
class AIReviewResult(BaseModel):
    summary: str = Field(..., description="A high-level executive summary of the changes")
    findings: List[ReviewFinding] = Field(default_factory=list, description="List of specific code issues found")
    security_score: int = Field(..., ge=0, le=100, description="0-100 score. 100 means perfectly secure.")
    is_blocking: bool = Field(False, description="If True, the AI recommends blocking the merge.")