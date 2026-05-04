from abc import ABC, abstractmethod
from typing import Dict, Any, List

from pydantic import BaseModel

from core.llm import HelloAgentsLLM

class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None

class Tool(ABC):
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, parameters: Dict[str, Any])->str:
        """执行工具"""
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """执行工具"""
        pass

    def __str__(self) -> str:
        return f"Tool(name={self.name})"


    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数"""
        required_params = [p.name for p in self.get_parameters() if p.required]
        return all(param in parameters for param in required_params)