"""Pipeline."""
from typing import List
from functools import cached_property
from openai import AsyncOpenAI
from pydantic import BaseModel
from .message import Message
from ..env_settings import OPENAI_API_KEY

class Pipeline(BaseModel):
    """"ML pipeline class."""
    @cached_property
    def openai_client(self) -> AsyncOpenAI:
        """OpenAI client."""
        return AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30,
            max_retries=2,
        )

    async def __call__(self, messages: List[Message]) -> Message:
        """Call method for pipeline."""
        return Message(
            role='assistant',
            content='how can I help you?'
        )
