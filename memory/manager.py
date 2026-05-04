import logging
from typing import Optional

from memory.base import MemoryConfig
from memory.types.working import WorkingMemory


logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器 - 统一的记忆操作接口

    负责：
    - 记忆生命周期管理
    - 记忆优先级和重要性评估
    - 记忆遗忘和清理机制
    - 多类型记忆的协调管理
    """

    def __init__(self, config: Optional[MemoryConfig] = None,
        user_id: str = "default_user",
        enable_working: bool = True,
        enable_episodic: bool = True,
        enable_semantic: bool = True,
        enable_perceptual: bool = False):

        self.config = config or MemoryConfig()
        self.user_id = user_id

        # 存储和检索功能已移至各记忆类型内部实现

        # 初始化各类型记忆
        self.memory_types = {}

        if enable_working:
            self.memory_types['working'] = WorkingMemory(self.config)

        logger.info(f"MemoryManager初始化完成，启用记忆类型: {list(self.memory_types.keys())}")


    def __str__(self) -> str:
        stats = self.get_memory_stats()
        return f"MemoryManager(user={self.user_id}, total={stats['total_memories']})"