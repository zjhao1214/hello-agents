from typing import Optional

from core.agent import Agent
from core.config import Config
from core.llm import HelloAgentsLLM
from core.message import MessageRole, Message


class SimpleAgent(Agent):
    """简单的对话Agent，支持可选的工具调用

    特性：
    - 纯对话模式（无工具）
    # - Function Calling 工具调用（可选）
    # - 自动多轮工具调用
    """
    def __int__(self, name:str, llm:HelloAgentsLLM, system_prompt: Optional[str]=None,
                config: Optional[Config] = None, tool_registry: Optional['ToolRegistry'] = None,
                enable_tool_call: bool = True, max_tool_iterations: int = 3):
        """
        初始化SimpleAgent

        Args:
            name: Agent名称
            llm: LLM实例
            system_prompt: 系统提示词
            config: 配置对象
            tool_registry: 工具注册表（可选，如果提供则启用工具调用）
            enable_tool_calling: 是否启用工具调用（只有在提供tool_registry时生效）
            max_tool_iterations: 最大工具调用迭代次数
        """

        super().__int__(self, name, llm, system_prompt, config, tool_registry)
        self.enable_tool_call = enable_tool_call
        self.max_tool_iterations = max_tool_iterations


    def run(self, input_text:str, **kwargs) -> str:
        """
               运行简单Agent

               Args:
                   input_text: 用户输入
                   **kwargs: 其他参数

               Returns:
                   Agent响应
               """
        messages = []
        if self.system_prompt:
            messages.append(Message(role="user", content=self.system_prompt))

        # 添加历史消息
        for msg in self._history:
            messages.append(Message(role=msg.role, content=msg.content))

        messages.append(Message(role="user", content=input_text))

        response = self.llm.invoke(messages)

        # 保存到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(response, "assistant"))

        return response