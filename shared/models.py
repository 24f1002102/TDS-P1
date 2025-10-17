"""
Shared models for the TDS Project.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Attachment(BaseModel):
    """Attachment in a task request."""
    name: str
    url: str


class TaskRequest(BaseModel):
    """Request sent to student API endpoint."""
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: List[Dict[str, str]] = Field(default_factory=list)


class RepoSubmission(BaseModel):
    """Submission sent to evaluation URL."""
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str


class EvaluationResult(BaseModel):
    """Result of a single check."""
    check: str
    score: float
    reason: str
    logs: str = ""
