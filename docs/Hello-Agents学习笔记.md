# Hello-Agents 学习笔记

## 《从零开始构建智能体》 — Datawhale 开源教程

---

## 一、智能体（Agent）基础

### 1.1 什么是智能体

智能体是能够通过**传感器**感知环境，通过**执行器**自主采取**行动**以实现特定目标的实体。

**四个核心要素**：
- **环境（Environment）** — Agent 运作的外部世界
- **传感器（Sensors）** — 感知环境状态（相机、麦克风、API 返回等）
- **执行器（Actuators）** — 执行具体操作
- **自主性（Autonomy）** — 自主决策和行动能力

### 1.2 智能体的类型

| 类型 | 特点 | 示例 |
|------|------|------|
| 单一 Agent | 独立完成任务 | ChatGPT |
| 多 Agent 系统 | 多个 Agent 协作 | 旅行助手、研究 Agent |

---

## 二、经典 Agent 范式

### 2.1 ReAct（推理+行动）

将"思考"与"执行"紧密耦合，Agent 边想边做，动态调整策略。

```python
# 核心循环
while not complete:
    thought = agent.think()    # 思考
    action = agent.act()       # 执行
    observation = env反馈()     # 观察结果
```

### 2.2 Plan-and-Solve（先计划后执行）

"三思而后行" — 先生成完整行动计划，再严格按计划执行。

### 2.3 Reflection（自我反思）

赋予 Agent"反思"能力，通过自我批评和纠正优化结果。

---

## 三、HelloAgents 框架设计

### 3.1 为什么要自建框架

| 问题 | 现有框架痛点 |
|------|-------------|
| 过度抽象 | LangChain 概念繁多，入门困难 |
| 迭代快 | API 经常变化，维护成本高 |
| 黑盒逻辑 | 核心逻辑封装过紧，难以深度定制 |
| 依赖复杂 | 大量依赖包，体积大，可能冲突 |

### 3.2 框架核心设计理念

1. **轻量级 + 教学友好** — 代码简洁可读，按章节分离核心代码
2. **基于标准 API** — 基于 OpenAI API 标准，方便迁移
3. **渐进式学习路径** — 每个版本可下载，逐步迭代
4. **统一 Tool 抽象** — Memory、RAG、MCP 等均为 Tool

### 3.3 框架架构

```
hello_agents/
├── core/                      # 核心框架层
│   ├── agent.py               # Agent 基类
│   ├── llm.py                 # HelloAgentsLLM 统一接口
│   ├── message.py            # 消息系统
│   └── config.py             # 配置管理
├── agents/                   # Agent 实现层
│   ├── simple_agent.py      # SimpleAgent
│   ├── react_agent.py        # ReActAgent
│   ├── reflection_agent.py   # ReflectionAgent
│   └── plan_solve_agent.py  # PlanAndSolveAgent
└── tools/                    # 工具系统层
    ├── base.py              # Tool 基类
    ├── registry.py          # Tool 注册机制
    └── builtin/             # 内置工具集
```

### 3.4 快速使用

```python
from hello_agents import SimpleAgent, HelloAgentsLLM

llm = HelloAgentsLLM()
agent = SimpleAgent(name="AI Assistant", llm=llm)

response = agent.run("Hello! Please introduce yourself")
print(response)
```

---

## 四、记忆系统（Memory）

### 4.1 为什么需要记忆

LLM 的两大局限：
1. **对话状态遗忘** — 无状态设计，无法记住之前对话
2. **内置知识局限** — 知识静态且有时效限制

### 4.2 人类记忆系统类比

| 记忆类型 | 人类对应 | 特点 |
|----------|----------|------|
| Working Memory | 短时记忆 | 临时信息，容量有限 |
| Episodic Memory |情景记忆 | 具体事件，时序检索 |
| Semantic Memory | 语义记忆 | 抽象知识，知识图谱 |
| Perceptual Memory | 感知记忆 | 多模态数据 |

### 4.3 HelloAgents 记忆系统架构

```
基础设施层
├── MemoryManager — 统一调度
├── MemoryItem — 标准化的记忆项
└── BaseMemory — 通用接口

记忆类型层
├── WorkingMemory — 工作记忆（TTL管理）
├── EpisodicMemory — 情景记忆（SQLite+Qdrant）
├── SemanticMemory — 语义记忆（Qdrant+Neo4j图数据库）
└── PerceptualMemory — 感知记忆（多模态）

存储后端层
├── QdrantVectorStore — 向量存储
├── Neo4jGraphStore — 图存储
└── SQLiteDocumentStore — 文档存储
```

### 4.4 四种记忆类型详解

#### Working Memory（工作记忆）

**定位**：Agent 的"短时记忆"，存储当前会话的上下文信息。

**特点**：
- 纯内存存储，访问速度极快
- 容量有限（默认50条）
- TTL（Time To Live）自动清理

**评分公式**：
```
最终得分 = (语义相似度 × 时间衰减) × (0.8 + 重要性 × 0.4)
```

#### Episodic Memory（情景记忆）

**定位**：长期存储具体交互事件和 Agent 的学习经验。

**特点**：
- SQLite + Qdrant 混合存储
- 支持时序和会话级检索

**评分公式**：
```
最终得分 = (向量相似度 × 0.8 + 时间新颖度 × 0.2) × (0.8 + 重要性 × 0.4)
```

#### Semantic Memory（语义记忆）

**定位**：存储抽象知识、概念和规则。

**特点**：
- Qdrant + Neo4j 混合架构
- 混合检索策略：向量 + 图 + 语义推理

**评分公式**：
```
最终得分 = (向量相似度 × 0.7 + 图相似度 × 0.3) × (0.8 + 重要性 × 0.4)
```

#### Perceptual Memory（感知记忆）

**定位**：处理多模态数据（图像、音频等），支持跨模态检索。

**特点**：
- 多模态编码器（Text/CLIP/CLAP）
- 分模态向量存储

**评分公式**：
```
最终得分 = (向量相似度 × 0.8 + 时间新颖度 × 0.2) × (0.8 + 重要性 × 0.4)
```

### 4.5 记忆操作

```python
# 添加记忆
memory_tool.execute("add",
    content="用户张三是一名Python开发者",
    memory_type="semantic",
    importance=0.8
)

# 搜索记忆
result = memory_tool.execute("search", query="Python开发者", limit=3)

# 遗忘（三种策略）
memory_tool.execute("forget", strategy="importance_based", threshold=0.2)
memory_tool.execute("forget", strategy="time_based", max_age_days=30)

# 记忆整合
memory_tool.execute("consolidate",
    from_type="working",
    to_type="episodic",
    importance_threshold=0.7
)
```

---

## 五、RAG（检索增强生成）

### 5.1 RAG 发展历程

| 阶段 | 时间 | 特点 |
|------|------|------|
| 朴素 RAG | 2020-2021 | TF-IDF/BM25 检索，直接拼接 |
| 高级 RAG | 2022-2023 | Dense Embedding，查询重写、重排序 |
| 模块化 RAG | 2023至今 | 混合检索、MQE、HyDE、链式推理 |

### 5.2 RAG 工作流程

```
数据准备阶段：数据提取 → 文本分块 → 向量化 → 存储
    ↓
应用阶段：用户查询 → 检索相关信息 → 注入Prompt → LLM生成
```

### 5.3 高级检索策略

#### MQE（多查询扩展）

通过生成语义等价的多样化查询提高检索召回率。

```
原查询："如何学习Python"
    ↓ LLM 扩展
├── "Python入门教程"
├── "Python学习方法"
└── "Python编程指南"
```

#### HyDE（假设文档嵌入）

"用答案找答案" — 先让 LLM 生成假设答案，再用这个答案去检索真实文档。

```
原查询："什么是机器学习"
    ↓ LLM 生成假设答案
假设答案："机器学习是人工智能的一个分支..."
    ↓ 向量检索
找到的真实文档
```

---

## 六、Agent 通信协议

### 6.1 三大协议对比

| 协议 | 解决什么问题 | 架构特点 |
|------|-------------|----------|
| **MCP** | Agent 如何调用外部工具/服务 | Host-Client-Server 三层 |
| **A2A** | Agent 之间如何对话协作 | 点对点通信 |
| **ANP** | 大规模 Agent 网络中如何发现服务 | 去中心化服务发现 |

### 6.2 MCP（Model Context Protocol）

**设计理念**：像 USB-C 统一设备连接一样，统一 Agent 与外部工具的交互方式。

**架构**：
```
User → Claude Desktop (Host) → MCP Client → MCP Server → 外部服务
```

**核心能力**：
- **Tools** — 主动执行操作
- **Resources** — 被动提供数据
- **Prompts** — 提供模板

### 6.3 A2A vs Function Calling

| | Function Calling | MCP |
|--|-----------------|-----|
| 本质 | LLM 内在能力（何时打电话） | 基础设施协议（电话通信标准） |
| 层次 | 模型决策层 | 工程连接层 |
| 关系 | **互补** | **互补** |

### 6.4 协议选择指南

- 需要调用外部 API/文件/数据库 → **MCP**
- 多 Agent 协作完成任务 → **A2A**
- 构建大型 Agent 生态系统 → **ANP**

---

## 七、综合案例：智能旅行助手

**项目结构**：
```
TravelAssistant/
├── router_agent.py        # 路由 Agent（任务分发）
├── flight_agent.py        # 机票 Agent
├── hotel_agent.py         # 酒店 Agent
├── attraction_agent.py    # 景点 Agent
└── mcp_servers/          # MCP 服务端
```

**协作流程**：
1. 用户提出需求 → Router Agent 接收
2. Router 分析任务类型，分发给专业 Agent
3. 各 Agent 调用不同 MCP Server 获取信息
4. 结果汇总返回给用户

---

## 八、学习路径建议

```
第一部分（1-3章）
└── 理论基础：智能体概念、发展史、LLM基础

第二部分（4-7章）
└── 动手实践：经典范式 → 低代码平台 → 框架开发 → 自研框架

第三部分（8-12章）
└── 高级知识：记忆/RAG、上下文工程、MCP/A2A协议、Agentic-RL、评估

第四部分（13-15章）
└── 综合案例：智能旅行助手、DeepResearch Agent、赛博小镇

第五部分（16章）
└── 毕业设计：构建完整多 Agent 应用
```

---

## 九、环境配置

```bash
# 安装 HelloAgents
pip install "hello-agents[all]==0.2.0"

# 下载语言模型
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm

# 配置 .env
# LLM API、Embedding、Qdrant、Neo4j 等
```

---

# Hello-Agents 学习笔记 — 第八章：记忆与检索系统（详细补充）

---

## 一、为什么 Agent 需要记忆

### 1.1 LLM 的两大局限

| 局限 | 问题描述 | 后果 |
|------|----------|------|
| **对话状态遗忘** | LLM 是无状态的，每次请求独立计算 | 无法记住之前的对话内容、用户偏好 |
| **内置知识局限** | 知识静态、来自训练数据、有截止日期 | 无法获取最新信息、缺乏领域深度知识 |

### 1.2 具体表现

```python
# 第一次对话
response1 = agent.run("我叫张三，学Python，已掌握基本语法")
# "Great! Python基本语法是编程的重要基础..."

# 第二次对话（新会话）
response2 = agent.run("你记得我的学习进度吗？")
# "抱歉，我不知道你的学习进度..."  ← 遗忘
```

---

## 二、人类记忆系统类比

### 2.1 记忆的层次结构

```
┌─────────────────────────────────────────────────────┐
│                   人类记忆系统                       │
├─────────────────────────────────────────────────────┤
│  感觉记忆 Sensory Memory                             │
│    - 时长：0.5-3秒                                   │
│    - 容量：巨大                                       │
│    - 功能：暂时存储所有感知信息                        │
├─────────────────────────────────────────────────────┤
│  工作记忆 Working Memory                            │
│    - 时长：15-30秒                                   │
│    - 容量：7±2 项                                    │
│    - 功能：当前任务的信息处理                          │
├─────────────────────────────────────────────────────┤
│  长期记忆 Long-term Memory                          │
│    ┌──────────────────┬──────────────────────────┐  │
│    │  程序性记忆       │  陈述性记忆              │  │
│    │  (技能、习惯)    │  (可用语言表达的知识)     │  │
│    │                  ├──────────┬─────────────┤  │
│    │                  │ 语义记忆  │ 情景记忆    │  │
│    │                  │ (一般知识) │ (个人经历) │  │
│    └──────────────────┴──────────┴─────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2.2 Agent 记忆系统的映射

| 人类记忆 | Agent 记忆 | 特点 |
|----------|------------|------|
| 工作记忆 | Working Memory | 临时信息，会话级，容量有限 |
| 情景记忆 | Episodic Memory | 具体事件，时序检索 |
| 语义记忆 | Semantic Memory | 抽象概念，知识图谱 |
| 感觉记忆 | Perceptual Memory | 多模态数据（图像、音频） |

---

## 三、记忆系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      HelloAgents 记忆系统                        │
├─────────────────────────────────────────────────────────────────┤
│  基础设施层 Infrastructure Layer                                 │
│  ├── MemoryManager — 统一调度和协调                             │
│  ├── MemoryItem — 标准化的记忆项数据结构                         │
│  ├── MemoryConfig — 配置管理                                    │
│  └── BaseMemory — 记忆基类（通用接口定义）                        │
├─────────────────────────────────────────────────────────────────┤
│  记忆类型层 Memory Types Layer                                   │
│  ├── WorkingMemory — 工作记忆（TTL管理，纯内存）                 │
│  ├── EpisodicMemory — 情景记忆（SQLite+Qdrant）                 │
│  ├── SemanticMemory — 语义记忆（Qdrant+Neo4j图数据库）          │
│  └── PerceptualMemory — 感知记忆（多模态，SQLite+Qdrant）        │
├─────────────────────────────────────────────────────────────────┤
│  存储后端层 Storage Backend Layer                                │
│  ├── QdrantVectorStore — 向量存储（高性能语义检索）               │
│  ├── Neo4jGraphStore — 图存储（知识图谱管理）                    │
│  └── SQLiteDocumentStore — 文档存储（结构化持久化）              │
├─────────────────────────────────────────────────────────────────┤
│  Embedding 服务层                                                │
│  ├── DashScopeEmbedding — 通义千问 embedding（云API）           │
│  ├── LocalTransformerEmbedding — 本地 embedding（离线部署）      │
│  └── TFIDFEmbedding — TFIDF embedding（轻量级备选）             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 四种记忆类型详解

#### 3.2.1 Working Memory（工作记忆）

**定位**：Agent 的"短时记忆"，存储当前会话的上下文信息。

**特点**：
- 纯内存存储，访问速度极快
- 容量有限（默认50条）
- TTL（Time To Live）自动清理
- 会话结束自动清除

**核心实现**：

```python
class WorkingMemory:
    def __init__(self, config: MemoryConfig):
        self.max_capacity = config.working_memory_capacity or 50  # 容量限制
        self.max_age_minutes = config.working_memory_ttl or 60    # TTL 60分钟
        self.memories = []

    def add(self, memory_item: MemoryItem) -> str:
        self._expire_old_memories()  # 过期清理
        
        if len(self.memories) >= self.max_capacity:
            self._remove_lowest_priority_memory()  # 容量管理
        
        self.memories.append(memory_item)
        return memory_item.id

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        self._expire_old_memories()
        
        # 混合检索：TF-IDF向量化 + 关键词匹配
        vector_scores = self._try_tfidf_search(query)
        
        # 综合评分
        scored_memories = []
        for memory in self.memories:
            vector_score = vector_scores.get(memory.id, 0.0)
            keyword_score = self._calculate_keyword_score(query, memory.content)
            
            # 混合评分：语义×0.7 + 关键词×0.3（如果向量化失败则全用关键词）
            base_relevance = vector_score * 0.7 + keyword_score * 0.3 if vector_score > 0 else keyword_score
            
            # 时间衰减
            time_decay = self._calculate_time_decay(memory.timestamp)
            
            # 重要性权重 [0.8, 1.2]
            importance_weight = 0.8 + (memory.importance * 0.4)
            
            # 最终得分 = 相似度 × 时间衰减 × 重要性权重
            final_score = base_relevance * time_decay * importance_weight
            if final_score > 0:
                scored_memories.append((final_score, memory))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:limit]]
```

**评分公式**：
```
最终得分 = (语义相似度 × 时间衰减) × (0.8 + 重要性 × 0.4)
```

---

#### 3.2.2 Episodic Memory（情景记忆）

**定位**：长期存储具体交互事件和 Agent 的学习经验。

**特点**：
- SQLite + Qdrant 混合存储
- 支持时序和会话级检索
- 结构化过滤 + 语义向量检索
- 保留丰富的上下文信息

**核心实现**：

```python
class EpisodicMemory:
    def add(self, memory_item: MemoryItem) -> str:
        # 创建情景对象
        episode = Episode(
            episode_id=memory_item.id,
            session_id=memory_item.metadata.get("session_id", "default"),
            timestamp=memory_item.timestamp,
            content=memory_item.content,
            context=memory_item.metadata
        )
        
        # 更新会话索引
        session_id = episode.session_id
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(episode.episode_id)
        
        # 持久化存储（SQLite + Qdrant）
        self._persist_episode(episode)
        return memory_item.id

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        # 1. 结构化预过滤（时间范围、重要性等）
        candidate_ids = self._structured_filter(**kwargs)
        
        # 2. 向量语义检索
        hits = self._vector_search(query, limit * 5, kwargs.get("user_id"))
        
        # 3. 综合评分和排序
        results = []
        for hit in hits:
            if self._should_include(hit, candidate_ids, kwargs):
                score = self._calculate_episode_score(hit)
                memory_item = self._create_memory_item(hit)
                results.append((score, memory_item))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:limit]]

    def _calculate_episode_score(self, hit) -> float:
        """情景记忆评分算法"""
        vec_score = float(hit.get("score", 0.0))
        recency_score = self._calculate_recency(hit["metadata"]["timestamp"])
        importance = hit["metadata"].get("importance", 0.5)
        
        # 评分公式：(向量相似度×0.8 + 时间新颖度×0.2) × 重要性权重
        base_relevance = vec_score * 0.8 + recency_score * 0.2
        importance_weight = 0.8 + (importance * 0.4)
        
        return base_relevance * importance_weight
```

**评分公式**：
```
最终得分 = (向量相似度 × 0.8 + 时间新颖度 × 0.2) × (0.8 + 重要性 × 0.4)
```

---

#### 3.2.3 Semantic Memory（语义记忆）

**定位**：存储抽象知识、概念和规则（如用户偏好、领域知识）。

**特点**：
- Qdrant + Neo4j 混合架构
- 向量检索用于快速语义匹配
- 图存储用于实体关系推理
- 混合检索策略：向量 + 图 + 语义推理

**核心实现**：

```python
class SemanticMemory(BaseMemory):
    def add(self, memory_item: MemoryItem) -> str:
        # 1. 生成文本嵌入
        embedding = self.embedding_model.encode(memory_item.content)
        
        # 2. 提取实体和关系
        entities = self._extract_entities(memory_item.content)
        relations = self._extract_relations(memory_item.content, entities)
        
        # 3. 存储到 Neo4j 图数据库
        for entity in entities:
            self._add_entity_to_graph(entity, memory_item)
        
        for relation in relations:
            self._add_relation_to_graph(relation, memory_item)
        
        # 4. 存储到 Qdrant 向量数据库
        metadata = {
            "memory_id": memory_item.id,
            "entities": [e.entity_id for e in entities],
            "entity_count": len(entities),
            "relation_count": len(relations)
        }
        
        self.vector_store.add_vectors(
            vectors=[embedding.tolist()],
            metadata=[metadata],
            ids=[memory_item.id]
        )

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        # 1. 向量检索
        vector_results = self._vector_search(query, limit * 2, user_id)
        
        # 2. 图检索
        graph_results = self._graph_search(query, limit * 2, user_id)
        
        # 3. 混合排名
        combined_results = self._combine_and_rank_results(
            vector_results, graph_results, query, limit
        )
        
        return combined_results[:limit]

    def _combine_and_rank_results(self, vector_results, graph_results, query, limit):
        """混合排名算法"""
        combined = {}
        
        # 合并向量和图检索结果
        for result in vector_results:
            combined[result["memory_id"]] = {
                **result,
                "vector_score": result.get("score", 0.0),
                "graph_score": 0.0
            }
        
        for result in graph_results:
            memory_id = result["memory_id"]
            if memory_id in combined:
                combined[memory_id]["graph_score"] = result.get("similarity", 0.0)
            else:
                combined[memory_id] = {
                    **result,
                    "vector_score": 0.0,
                    "graph_score": result.get("similarity", 0.0)
                }
        
        # 计算混合分数
        for memory_id, result in combined.items():
            vector_score = result["vector_score"]
            graph_score = result["graph_score"]
            importance = result.get("importance", 0.5)
            
            # 基础相关性：(向量相似度×0.7 + 图相似度×0.3)
            base_relevance = vector_score * 0.7 + graph_score * 0.3
            
            # 重要性权重 [0.8, 1.2]
            importance_weight = 0.8 + (importance * 0.4)
            
            # 最终分数
            combined[memory_id]["combined_score"] = base_relevance * importance_weight
        
        # 排序返回
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        return sorted_results[:limit]
```

**评分公式**：
```
最终得分 = (向量相似度 × 0.7 + 图相似度 × 0.3) × (0.8 + 重要性 × 0.4)
```

---

#### 3.2.4 Perceptual Memory（感知记忆）

**定位**：处理多模态数据（图像、音频等），支持跨模态检索。

**特点**：
- 多模态编码器（Text/CLIP/CLAP）
- 分模态向量存储（避免维度不匹配）
- 支持跨模态相似性搜索
- 时间衰减采用指数衰减模型

**核心实现**：

```python
class PerceptualMemory(BaseMemory):
    def __init__(self, config: MemoryConfig, storage_backend=None):
        super().__init__(config, storage_backend)
        
        # 多模态编码器
        self.text_embedder = get_text_embedder()
        self._clip_model = self._init_clip_model()   # 图像编码
        self._clap_model = self._init_clap_model()  # 音频编码
        
        # 分模态向量存储
        self.vector_stores = {
            "text": QdrantConnectionManager.get_instance(
                collection_name="perceptual_text",
                vector_size=self.vector_dim
            ),
            "image": QdrantConnectionManager.get_instance(
                collection_name="perceptual_image",
                vector_size=self._image_dim
            ),
            "audio": QdrantConnectionManager.get_instance(
                collection_name="perceptual_audio",
                vector_size=self._audio_dim
            )
        }

    def _calculate_recency_score(self, timestamp: str) -> float:
        """计算时间新颖度分数（指数衰减）"""
        try:
            memory_time = datetime.fromisoformat(timestamp)
            current_time = datetime.now()
            age_hours = (current_time - memory_time).total_seconds() / 3600
            
            # 指数衰减：24小时内保持高分，之后逐渐衰减
            decay_factor = 0.1
            recency_score = math.exp(-decay_factor * age_hours / 24)
            
            return max(0.1, recency_score)  # 最低保持0.1基础分
        except Exception:
            return 0.5  # 默认中等分数
```

**评分公式**：
```
最终得分 = (向量相似度 × 0.8 + 时间新颖度 × 0.2) × (0.8 + 重要性 × 0.4)
```

---

## 四、记忆操作详解

### 4.1 MemoryTool 核心操作

```python
class MemoryTool(Tool):
    def execute(self, action: str, **kwargs) -> str:
        """执行记忆操作"""
        if action == "add":
            return self._add_memory(**kwargs)
        elif action == "search":
            return self._search_memory(**kwargs)
        elif action == "summary":
            return self._get_summary(**kwargs)
        elif action == "stats":
            return self._get_stats(**kwargs)
        elif action == "update":
            return self._update_memory(**kwargs)
        elif action == "remove":
            return self._remove_memory(**kwargs)
        elif action == "forget":
            return self._forget(**kwargs)
        elif action == "consolidate":
            return self._consolidate(**kwargs)
        elif action == "clear_all":
            return self._clear_all(**kwargs)
```

### 4.2 add — 添加记忆

```python
def _add_memory(
    self,
    content: str = "",
    memory_type: str = "working",
    importance: float = 0.5,
    file_path: str = None,
    modality: str = None,
    **metadata
) -> str:
    """添加记忆"""
    # 1. 自动管理会话ID
    if self.current_session_id is None:
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 2. 感知记忆的文件支持
    if memory_type == "perceptual" and file_path:
        inferred = modality or self._infer_modality(file_path)
        metadata.setdefault("modality", inferred)
        metadata.setdefault("raw_data", file_path)
    
    # 3. 添加上下文信息
    metadata.update({
        "session_id": self.current_session_id,
        "timestamp": datetime.now().isoformat()
    })
    
    memory_id = self.memory_manager.add_memory(
        content=content,
        memory_type=memory_type,
        importance=importance,
        metadata=metadata,
        auto_classify=False
    )
    
    return f"✅ Memory added (ID: {memory_id[:8]}...)"
```

**使用示例**：

```python
# 1. 工作记忆 - 临时信息
memory_tool.execute("add",
    content="用户刚问了一个关于Python函数的问题",
    memory_type="working",
    importance=0.6
)

# 2. 情景记忆 - 具体事件
memory_tool.execute("add",
    content="2024年3月15日，用户张三完成了第一个Python项目",
    memory_type="episodic",
    importance=0.8,
    event_type="milestone",
    location="在线学习平台"
)

# 3. 语义记忆 - 抽象知识
memory_tool.execute("add",
    content="Python是一种解释型、面向对象的编程语言",
    memory_type="semantic",
    importance=0.9,
    knowledge_type="factual"
)

# 4. 感知记忆 - 多模态信息
memory_tool.execute("add",
    content="用户上传了一张包含函数定义的Python代码截图",
    memory_type="perceptual",
    importance=0.7,
    modality="image",
    file_path="./uploads/code_screenshot.png"
)
```

---

### 4.3 search — 搜索记忆

```python
def _search_memory(
    self,
    query: str,
    limit: int = 5,
    memory_types: List[str] = None,
    memory_type: str = None,
    min_importance: float = 0.1
) -> str:
    """搜索记忆"""
    # 参数标准化
    if memory_type and not memory_types:
        memory_types = [memory_type]
    
    results = self.memory_manager.retrieve_memories(
        query=query,
        limit=limit,
        memory_types=memory_types,
        min_importance=min_importance
    )
    
    if not results:
        return f"🔍 No memories found related to '{query}'"
    
    # 格式化结果
    formatted_results = []
    formatted_results.append(f"🔍 Found {len(results)} related memories:")
    
    for i, memory in enumerate(results, 1):
        memory_type_label = {
            "working": "Working Memory",
            "episodic": "Episodic Memory",
            "semantic": "Semantic Memory",
            "perceptual": "Perceptual Memory"
        }.get(memory.memory_type, memory.memory_type)
        
        content_preview = memory.content[:80] + "..." if len(memory.content) > 80 else memory.content
        formatted_results.append(
            f"{i}. [{memory_type_label}] {content_preview} (Importance: {memory.importance:.2f})"
        )
    
    return "\n".join(formatted_results)
```

**使用示例**：

```python
# 基本搜索
result = memory_tool.execute("search", query="Python编程", limit=5)

# 指定记忆类型搜索
result = memory_tool.execute("search",
    query="学习进度",
    memory_type="episodic",
    limit=3
)

# 多类型搜索
result = memory_tool.execute("search",
    query="函数定义",
    memory_types=["semantic", "episodic"],
    min_importance=0.5
)
```

---

### 4.4 forget — 遗忘机制

遗忘机制是最具认知科学特色的功能，模拟人脑的选择性遗忘过程。

```python
def _forget(self, strategy: str = "importance_based", threshold: float = 0.1, max_age_days: int = 30) -> str:
    """遗忘记忆（支持多种策略）"""
    count = self.memory_manager.forget_memories(
        strategy=strategy,
        threshold=threshold,
        max_age_days=max_age_days
    )
    return f"🧹 Forgot {count} memories (strategy: {strategy})"
```

**三种遗忘策略**：

| 策略 | 说明 | 使用场景 |
|------|------|----------|
| `importance_based` | 删除重要性低于阈值的记忆 | 清理低价值信息 |
| `time_based` | 删除超过指定天数的记忆 | 定期清理过期信息 |
| `capacity_based` | 容量满时删除最不重要的记忆 | 控制存储成本 |

**使用示例**：

```python
# 1. 基于重要性的遗忘
memory_tool.execute("forget",
    strategy="importance_based",
    threshold=0.2
)

# 2. 基于时间的遗忘
memory_tool.execute("forget",
    strategy="time_based",
    max_age_days=30
)

# 3. 基于容量的遗忘
memory_tool.execute("forget",
    strategy="capacity_based",
    threshold=0.3
)
```

---

### 4.5 consolidate — 记忆整合

将短时记忆转换为长时记忆，模拟人脑的记忆巩固过程。

```python
def _consolidate(self, from_type: str = "working", to_type: str = "episodic", importance_threshold: float = 0.7) -> str:
    """整合记忆（将重要的短时记忆提升为长时记忆）"""
    count = self.memory_manager.consolidate_memories(
        from_type=from_type,
        to_type=to_type,
        importance_threshold=importance_threshold,
    )
    return f"🔄 Consolidated {count} memories to long-term memory ({from_type} → {to_type}, threshold={importance_threshold})"
```

**使用示例**：

```python
# 将重要的工作记忆转换为情景记忆
memory_tool.execute("consolidate",
    from_type="working",
    to_type="episodic",
    importance_threshold=0.7
)

# 将重要的情景记忆转换为语义记忆
memory_tool.execute("consolidate",
    from_type="episodic",
    to_type="semantic",
    importance_threshold=0.8
)
```

---

## 五、RAG 系统（检索增强生成）

### 5.1 RAG 发展历程

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG 发展三阶段                           │
├─────────────────────────────────────────────────────────────────┤
│  第一阶段：朴素 RAG（2020-2021）                                 │
│  ├── 检索方法：TF-IDF / BM25（关键词匹配）                        │
│  └── 生成模式：直接拼接检索结果到 prompt                          │
├─────────────────────────────────────────────────────────────────┤
│  第二阶段：高级 RAG（2022-2023）                                 │
│  ├── 检索方法：Dense Embedding（语义检索）                        │
│  └── 生成模式：查询重写、文档分块、重排序等优化                   │
├─────────────────────────────────────────────────────────────────┤
│  第三阶段：模块化 RAG（2023至今）                                │
│  ├── 检索方法：混合检索、多查询扩展、HyDE 等                       │
│  └── 生成模式：链式推理、自我反思纠正等                           │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 RAG 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG 系统工作流程                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ 数据准备阶段 │ →  │ 应用阶段    │    │ 生成阶段    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
│  1. 数据提取    ──────────────────────────────────────────────────│
│  2. 文本分块    ──────────────────────────────────────────────────│
│  3. 向量化      ──────────────────────────────────────────────────│
│                        ↓                                         │
│                    用户查询                                       │
│                        ↓                                         │
│                   检索相关信息                                    │
│                        ↓                                         │
│                   注入到 Prompt                                  │
│                        ↓                                         │
│                   LLM 生成答案                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 HelloAgents RAG 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      HelloAgents RAG 系统                       │
├─────────────────────────────────────────────────────────────────┤
│  用户层：RAGTool 统一入口                                        │
├─────────────────────────────────────────────────────────────────┤
│  应用层：智能问答、搜索、管理                                     │
├─────────────────────────────────────────────────────────────────┤
│  处理层：文档解析、分块、向量化                                    │
├─────────────────────────────────────────────────────────────────┤
│  存储层：向量数据库、文档存储                                      │
├─────────────────────────────────────────────────────────────────┤
│  基础层：Embedding 模型、LLM、数据库                              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 文档处理流程

```
任意格式文档 → MarkItDown转换 → Markdown文本 → 智能分块 → 向量化 → 存储检索
```

**MarkItDown 支持的格式**：

| 类别 | 格式 |
|------|------|
| 文档 | PDF, Word, Excel, PowerPoint |
| 图像 | JPG, PNG, GIF（通过OCR） |
| 音频 | MP3, WAV, M4A（通过转录） |
| 文本 | TXT, CSV, JSON, XML, HTML |
| 代码 | Python, JavaScript, Java 等 |

### 5.5 智能分块策略

Markdown 结构感知分块流程：

```
标准 Markdown → 标题层级解析 → 段落语义分割 → Token计算分块 → 重叠策略优化 → 向量化准备
```

**分块算法**：

```python
def _chunk_paragraphs(paragraphs: List[Dict], chunk_tokens: int, overlap_tokens: int) -> List[Dict]:
    """基于 Token 数的智能分块"""
    chunks: List[Dict] = []
    cur: List[Dict] = []
    cur_tokens = 0
    i = 0
    
    while i < len(paragraphs):
        p = paragraphs[i]
        p_tokens = _approx_token_len(p["content"]) or 1
        
        if cur_tokens + p_tokens <= chunk_tokens or not cur:
            cur.append(p)
            cur_tokens += p_tokens
            i += 1
        else:
            # 生成当前块
            content = "\n\n".join(x["content"] for x in cur)
            chunks.append({
                "content": content,
                "start": cur[0]["start"],
                "end": cur[-1]["end"],
                "heading_path": next((x["heading_path"] for x in reversed(cur) if x.get("heading_path")), None),
            })
            
            # 构建重叠部分
            if overlap_tokens > 0 and cur:
                kept: List[Dict] = []
                kept_tokens = 0
                for x in reversed(cur):
                    t = _approx_token_len(x["content"]) or 1
                    if kept_tokens + t > overlap_tokens:
                        break
                    kept.append(x)
                    kept_tokens += t
                cur = list(reversed(kept))
                cur_tokens = kept_tokens
            else:
                cur = []
                cur_tokens = 0
    
    # 处理最后一块
    if cur:
        content = "\n\n".join(x["content"] for x in cur)
        chunks.append({
            "content": content,
            "start": cur[0]["start"],
            "end": cur[-1]["end"],
            "heading_path": next((x["heading_path"] for x in reversed(cur) if x.get("heading_path")), None),
        })
    
    return chunks
```

---

## 六、高级检索策略

### 6.1 MQE（多查询扩展）

**原理**：通过生成语义等价的多样化查询提高检索召回率。

```
原查询："如何学习Python"
    ↓ LLM 扩展
├── "Python入门教程"
├── "Python学习方法"
└── "Python编程指南"
    ↓ 并行检索
结果合并去重
```

**实现**：

```python
def _prompt_mqe(query: str, n: int) -> List[str]:
    """使用 LLM 生成多样化查询扩展"""
    llm = HelloAgentsLLM()
    prompt = [
        {"role": "system", "content": "你是一个检索查询扩展助手。生成语义等价或互补的多样化查询。"},
        {"role": "user", "content": f"原始查询: {query}\n请提供{n}个不同表述的查询，每行一个。"}
    ]
    text = llm.invoke(prompt)
    lines = [ln.strip("- \t") for ln in (text or "").splitlines()]
    return [ln for ln in lines if ln][:n] or [query]
```

### 6.2 HyDE（假设文档嵌入）

**原理**："用答案找答案" — 先让 LLM 生成假设答案段落，再用这个答案去检索真实文档。

```
原查询："什么是机器学习"
    ↓ LLM 生成假设答案
假设答案："机器学习是人工智能的一个分支，它使用算法让计算机从数据中学习模式..."
    ↓ 向量检索
找到的真实文档
```

**实现**：

```python
def _prompt_hyde(query: str) -> Optional[str]:
    """生成假设文档以改进检索"""
    llm = HelloAgentsLLM()
    prompt = [
        {"role": "system", "content": "基于用户的问题，先写一个可能的答案段落，用于向量检索中的查询文档。"},
        {"role": "user", "content": f"问题: {query}\n请直接写一个包含关键术语的客观中等长度段落。"}
    ]
    return llm.invoke(prompt)
```

### 6.3 扩展检索框架

```python
def search_vectors_expanded(
    query: str = "",
    top_k: int = 8,
    enable_mqe: bool = False,
    mqe_expansions: int = 2,
    enable_hyde: bool = False,
    candidate_pool_multiplier: int = 4,  # 候选池扩大倍数
) -> List[Dict]:
    """
    扩展检索：三步"扩展-检索-合并"工作流程
    """
    # 1. 生成扩展查询
    expanded_queries = [query]
    
    if enable_mqe:
        expanded_queries.extend(_prompt_mqe(query, mqe_expansions))
    
    hyde_doc = None
    if enable_hyde:
        hyde_doc = _prompt_hyde(query)
        if hyde_doc:
            expanded_queries.append(hyde_doc)
    
    # 2. 并行向量检索
    all_hits = []
    for q in expanded_queries:
        hits = vector_store.search(q, limit=top_k * candidate_pool_multiplier)
        all_hits.extend(hits)
    
    # 3. 合并去重排序
    merged = {}
    for hit in all_hits:
        memory_id = hit["memory_id"]
        if memory_id not in merged:
            merged[memory_id] = hit
    
    # 按分数排序返回 top_k
    sorted_results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:top_k]
```

---

## 七、快速使用示例

### 7.1 记忆系统快速体验

```python
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool

# 创建 Agent
llm = HelloAgentsLLM()
agent = SimpleAgent(name="Memory Assistant", llm=llm)

# 创建记忆工具
memory_tool = MemoryTool(user_id="user123")
tool_registry = ToolRegistry()
tool_registry.register_tool(memory_tool)
agent.tool_registry = tool_registry

# 添加多条记忆
memory_tool.execute("add",
    content="用户张三是一名Python开发者，专注于机器学习和数据分析",
    memory_type="semantic",
    importance=0.8
)

memory_tool.execute("add",
    content="用户李四是前端工程师，擅长React和Vue.js开发",
    memory_type="semantic",
    importance=0.7
)

# 搜索记忆
result = memory_tool.execute("search", query="Python开发者", limit=3)
print(result)

# 获取记忆摘要
result = memory_tool.execute("summary")
print(result)
```

### 7.2 RAG 系统快速体验

```python
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import RAGTool

# 创建 Agent
llm = HelloAgentsLLM()
agent = SimpleAgent(name="Knowledge Assistant", llm=llm)

# 创建 RAG 工具
rag_tool = RAGTool(
    knowledge_base_path="./knowledge_base",
    collection_name="test_collection",
    rag_namespace="test"
)

tool_registry = ToolRegistry()
tool_registry.register_tool(rag_tool)
agent.tool_registry = tool_registry

# 添加知识
rag_tool.execute("add_text",
    text="Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。",
    document_id="python_intro"
)

rag_tool.execute("add_text",
    text="机器学习是人工智能的一个分支，使用算法让计算机从数据中学习模式。",
    document_id="ml_basics"
)

# 搜索知识
result = rag_tool.execute("search",
    query="Python历史",
    limit=3,
    min_score=0.1
)
print(result)

# 知识库统计
result = rag_tool.execute("stats")
print(result)
```

---

## 八、评分公式汇总

| 记忆类型 | 评分公式 |
|----------|----------|
| Working Memory | `(语义相似度 × 时间衰减) × (0.8 + 重要性 × 0.4)` |
| Episodic Memory | `(向量相似度 × 0.8 + 时间新颖度 × 0.2) × (0.8 + 重要性 × 0.4)` |
| Semantic Memory | `(向量相似度 × 0.7 + 图相似度 × 0.3) × (0.8 + 重要性 × 0.4)` |
| Perceptual Memory | `(向量相似度 × 0.8 + 时间新颖度 × 0.2) × (0.8 + 重要性 × 0.4)` |

---

## 参考链接

- 官方文档：https://datawhalechina.github.io/hello-agents/
- GitHub：https://github.com/datawhalechina/Hello-Agents
- 自研框架 HelloAgents：https://github.com/jjyaoao/helloagents
- PDF 下载：https://github.com/datawhalechina/hello-agents/releases/latest
