from typing import List, Dict, Any

from memory.base import MemoryConfig
from tools.base import Tool, ToolParameter


class MemoryTool(Tool):

    def __init__(self,
                 user_id: str = "default_user",
                 memory_config: MemoryConfig = None,
                 memory_types: List[str] = None
                 ):
        super().__init__(
            name="memory",
            description="记忆工具 - 可以存储和检索对话历史、知识和经验")

        self.memory_config: MemoryConfig = memory_config or MemoryConfig()
        self.memory_types = memory_types or ["working", "episodic", "semantic"]


    def run(self, parameters: Dict[str, Any]) -> str:
        """执行工具 - Tool基类要求的接口

                Args:
                    parameters: 工具参数字典，必须包含action参数

                Returns:
                    执行结果字符串
                """
        if not self.validate_parameters(parameters):
            return "❌ 参数验证失败：缺少必需的参数"
        action = parameters.get("action")
        # 移除action参数，传递其余参数给execute方法
        kwargs = {k: v for k, v in parameters.items() if k != "action"}

        return self.execute(action, **kwargs)

    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数定义 - Tool基类要求的接口"""
        return [
            ToolParameter(
                name="action",
                type="string",
                description=(
                    "要执行的操作："
                    "add(添加记忆), search(搜索记忆), summary(获取摘要), stats(获取统计), "
                    "update(更新记忆), remove(删除记忆), forget(遗忘记忆), consolidate(整合记忆), clear_all(清空所有记忆)"
                ),
                required=True
            ),
            ToolParameter(name="content", type="string", description="记忆内容（add/update时可用；感知记忆可作描述）",
                          required=False),
            ToolParameter(name="query", type="string", description="搜索查询（search时可用）", required=False),
            ToolParameter(name="memory_type", type="string",
                          description="记忆类型：working, episodic, semantic, perceptual（默认：working）", required=False,
                          default="working"),
            ToolParameter(name="importance", type="number", description="重要性分数，0.0-1.0（add/update时可用）",
                          required=False),
            ToolParameter(name="limit", type="integer", description="搜索结果数量限制（默认：5）", required=False,
                          default=5),
            ToolParameter(name="memory_id", type="string", description="目标记忆ID（update/remove时必需）",
                          required=False),
            ToolParameter(name="file_path", type="string", description="感知记忆：本地文件路径（image/audio）",
                          required=False),
            ToolParameter(name="modality", type="string",
                          description="感知记忆模态：text/image/audio（不传则按扩展名推断）", required=False),
            ToolParameter(name="strategy", type="string",
                          description="遗忘策略：importance_based/time_based/capacity_based（forget时可用）",
                          required=False, default="importance_based"),
            ToolParameter(name="threshold", type="number", description="遗忘阈值（forget时可用，默认0.1）", required=False,
                          default=0.1),
            ToolParameter(name="max_age_days", type="integer", description="最大保留天数（forget策略为time_based时可用）",
                          required=False, default=30),
            ToolParameter(name="from_type", type="string", description="整合来源类型（consolidate时可用，默认working）",
                          required=False, default="working"),
            ToolParameter(name="to_type", type="string", description="整合目标类型（consolidate时可用，默认episodic）",
                          required=False, default="episodic"),
            ToolParameter(name="importance_threshold", type="number", description="整合重要性阈值（默认0.7）",
                          required=False, default=0.7),
        ]

    def execute(self, action: str, **kwargs) -> str:
        """执行记忆操作

        支持的操作：
        - add: 添加记忆
        - search: 搜索记忆
        - summary: 获取记忆摘要
        - stats: 获取统计信息
        """

        if action == "add":
            return self._add_memory(**kwargs)

        # TODO
        else:
            return f"不支持的操作: {action}。支持的操作: add, search, summary, stats, update, remove, forget, consolidate, clear_all"

    def _add_memory(self,
        content: str = "",
        memory_type: str = "working",
        importance: float = 0.5,
        file_path: str = None,
        modality: str = None,
        **metadata):
        """添加记忆"""
        try:
            
        except Exception as e:
            return f"❌ 添加记忆失败: {str(e)}"