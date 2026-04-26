from datetime import datetime
from typing import Literal, Optional, Any

from pydantic import BaseModel


MessageRole = Literal["user", "assistant", "system", "tool"]

class Message(BaseModel):
    """消息类"""
    def __init__(self,):
        content: str
        role: MessageRole
        timestamp: datetime = None
        metadata: Optional[dict[str, Any]] = None

        def __init__(self, content: str, role: MessageRole, **kwargs):
            super().__init__(
                content=content,
                role=role,
                timestamp=kwargs.get('timestamp', datetime.now()),
                metadata=kwargs.get('metadata', {})
            )

        def to_dict(self) -> dict[str, Any]:
            """转换为字典格式（OpenAI API格式）"""
            return {
                "role": self.role,
                "content": self.content
            }

        def __str__(self) -> str:
            return f"[{self.role}] {self.content}"