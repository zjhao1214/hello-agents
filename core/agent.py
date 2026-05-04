from abc import ABC, abstractmethod
from typing import Optional

from core.config import Config
from core.llm import HelloAgentsLLM
from core.message import Message

"""
ABC = Abstract Base Class（抽象基类）
专门用来当父类，不能直接创建对象。
@abstractmethod = 抽象方法装饰器
加在方法上，子类必须重写实现这个方法，否则报错。
"""
class Agent(ABC):
    """Agent基类"""

    def __init__(self, name:str, llm: HelloAgentsLLM,
                 system_prompt: Optional[str] = None,
                 config: Optional[Config] = None,):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: list[Message] = []

    @abstractmethod
    def run(self, input_text:str, **kwargs) ->str:
        """运行Agent"""
        pass

    def add_message(self, message: Message):
        self._history.append(message)

    def clear_history(self):
        """清空历史记录"""
        self._history.clear()

    def get_history(self) -> list[Message]:
        """获取历史记录"""
        return self._history.copy()

    def __str__(self):
        return f"Agent(name={self.name}, provider={self.llm.provider})"

