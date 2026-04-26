import os
from typing import Optional, Any

from pydantic import BaseModel


class Config(BaseModel):
    """HelloAgents配置类"""
    # LLM配置
    default_model: str = "MiniMax-M2.5"
    default_provider: str = "openai"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # 系统配置
    debug: bool = False
    log_level: str = "INFO"

    # 其他配置
    max_history_length: int = 100

    @classmethod
    def get_env(cls):
        return cls(
            debug=os.environ.get("DEBUG", False),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS")) if os.getenv("MAX_TOKENS") else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return self.to_dict()
