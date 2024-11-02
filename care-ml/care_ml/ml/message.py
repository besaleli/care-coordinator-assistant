"""Message models."""
from enum import StrEnum
from pydantic import BaseModel

class Role(StrEnum):
    """Message role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Message"""
    content: str
    role: Role
