"""Debug endpoints."""
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter
from ..models import Patient
from ..ml.message import Role, Message

router = APIRouter()

class PromptRequest(BaseModel):
    """Prompt request."""
    template_id: str
    role: Role
    prompt_kwargs: Optional[dict] = None

@router.get('/user')
def patient() -> Patient:
    """Test API retrieval of patient data."""
    return Patient.get_by_id(1).model_dump()

@router.post('/prompt')
def prompt(data: PromptRequest) -> Message:
    """Test prompt rendering."""
    return Message.from_template(
        data.template_id,
        data.role,
        prompt_kwargs=data.prompt_kwargs
        )
