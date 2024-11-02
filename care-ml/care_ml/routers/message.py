"""Message endpoints."""
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter
from ..ml.message import Message
from ..ml.services import PIPELINE


class MessageRequest(BaseModel):
    """Message request"""
    messages: List[Message]


class MessageResponse(BaseModel):
    """Message response"""
    message: Message


router = APIRouter()

@router.post('/create')
async def message(msg: MessageRequest) -> MessageResponse:
    """Message endpoint."""
    return MessageResponse(
        message=await PIPELINE(msg.messages)
    )
