"""Message models."""
from typing import List, Optional
from functools import cached_property
from importlib import resources as ir
from enum import StrEnum
import jinja2 as j2
from pydantic import BaseModel, RootModel

JINJA_ENV = j2.Environment()
PROMPTS_PATH = 'care_ml.prompts'

class Role(StrEnum):
    """Message role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Message"""
    content: str
    role: Role

    def switch(self) -> 'Message':
        """Switch role."""
        if self.role == Role.USER:
            return Message(role=Role.ASSISTANT, content=self.content)
        if self.role == Role.ASSISTANT:
            return Message(role=Role.USER, content=self.content)

        return self

    @staticmethod
    def from_template(
        template_id: str,
        role: Role,
        prompt_kwargs: Optional[dict] = None
        ) -> 'Message':
        """New message from template."""
        with ir.path(PROMPTS_PATH, f"{template_id}.j2") as path:
            text = (
                JINJA_ENV
                .from_string(path.read_text(encoding='utf-8'))
                .render(prompt_kwargs or {})
                )

        return Message(role=role, content=text)


class ChatHistory(RootModel[List[Message]]):
    """Message history"""
    @cached_property
    def _env(self) -> j2.Environment:
        return j2.Environment()

    def __getitem__(self, index: int) -> Message:
        return self.root[index]

    def append(self, message: Message) -> None:
        """Add message to history."""
        if message.role == Role.SYSTEM:
            raise ValueError("Chat history must not contain a system message")

        self.root.append(message)

    def switch(self) -> 'ChatHistory':
        """Switch role of all messages in history."""
        return ChatHistory([i.switch() for i in iter(self.root)])

    def render(
        self,
        system_prompt_id: Optional[str] = None,
        system_kwargs: Optional[dict] = None,
        user_prompt_id: Optional[str] = None,
        user_kwargs: Optional[dict] = None
        ) -> List[dict]:
        """Add system message to history."""
        messages = []

        if system_prompt_id:
            messages.append(
                Message
                .from_template(system_prompt_id, Role.SYSTEM, prompt_kwargs=system_kwargs)
                .model_dump()
                )

        if self.root:
            messages.extend(self.model_dump())

        if user_prompt_id:
            messages.append(
                Message
                .from_template(user_prompt_id, Role.USER, prompt_kwargs=user_kwargs)
                .model_dump()
                )

        return messages
