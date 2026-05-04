import json
import os.path
import sqlite3
import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

from memory.base import MemoryConfig


class DocumentStage(ABC):
    @abstractmethod
    def add_memory(
        self,
        memory_id: str,
        user_id: str,
        content: str,
        memory_type: str,
        timestamp: int,
        importance: float,
        properties: Dict[str, Any] = None
    ) -> str:
        """添加记忆"""
        pass

    @abstractmethod
    def search_memories(
            self,
            user_id: Optional[str] = None,
            memory_type: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            importance_threshold: Optional[float] = None,
            limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索记忆"""
        pass

    @abstractmethod
    def update_memory(
            self,
            memory_id: str,
            content: str = None,
            importance: float = None,
            properties: Dict[str, Any] = None
    ) -> bool:
        """更新记忆"""
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        pass

    @abstractmethod
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        pass

    @abstractmethod
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """添加文档"""
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """获取文档"""
        pass

class SQLiteDocumentStore(DocumentStage):

    def search_memories(self, user_id: Optional[str] = None, memory_type: Optional[str] = None,
                        start_time: Optional[int] = None, end_time: Optional[int] = None,
                        importance_threshold: Optional[float] = None, limit: int = 10) -> List[Dict[str, Any]]:
        pass

    def update_memory(self, memory_id: str, content: str = None, importance: float = None,
                      properties: Dict[str, Any] = None) -> bool:
        pass

    def delete_memory(self, memory_id: str) -> bool:
        pass

    def get_database_stats(self) -> Dict[str, Any]:
        def get_database_stats(self) -> Dict[str, Any]:
            """获取数据库统计信息"""
            conn = self._get_connection()
            cursor = conn.cursor()

            stats = {}

            # 统计各表的记录数
            tables = ["users", "memories", "concepts", "memory_concepts", "concept_relationships"]
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()["count"]

            # 统计记忆类型分布
            cursor.execute("""
                           SELECT memory_type, COUNT(*) as count
                           FROM memories
                           GROUP BY memory_type
                           """)
            memory_types = {}
            for row in cursor.fetchall():
                memory_types[row["memory_type"]] = row["count"]
            stats["memory_types"] = memory_types

            # 统计用户分布
            cursor.execute("""
                           SELECT user_id, COUNT(*) as count
                           FROM memories
                           GROUP BY user_id
                           ORDER BY count DESC
                               LIMIT 10
                           """)
            top_users = {}
            for row in cursor.fetchall():
                top_users[row["user_id"]] = row["count"]
            stats["top_users"] = top_users

            stats["store_type"] = "sqlite"
            stats["db_path"] = self.db_path

            return stats

    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """添加文档"""
        import uuid
        import time

        doc_id = str(uuid.uuid4())
        user_id = metadata.get("user_id", "system") if metadata else "system"

        return self.add_memory(
            memory_id=doc_id,
            user_id=user_id,
            content=content,
            memory_type="document",
            timestamp=int(time.time()),
            importance=0.5,
            properties=metadata or {}
        )

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        pass

    _instances = {}  # 存储已创建的实例
    _initialized_dbs = set()  # 存储已初始化的数据库路径

    def add_memory(self, memory_id: str, user_id: str, content: str, memory_type: str, timestamp: int,
                   importance: float, properties: Dict[str, Any] = None) -> str:
        """添加记忆"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 确保用户存在
        cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (user_id, user_id))

        # 插入记忆
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, user_id, content, memory_type, timestamp, importance, properties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            memory_id,
            user_id,
            content,
            memory_type,
            timestamp,
            importance,
            json.dumps(properties) if properties else None
        ))

        conn.commit()
        return memory_id


    def __init__(self, db_path: str = "./memory.db"):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self.db_path = db_path
        self.local = threading.local()

        # 初始化数据库（只初始化一次）
        abs_path = os.path.abspath(db_path)
        if abs_path not in self._initialized_dbs:
            self._init_database()
            self._initialized_dbs.add(abs_path)
            print(f"[OK] SQLite 文档存储初始化完成: {db_path}")

        self._initialized = True

    def __new__(cls, db_path: str = "./memory.db"):
        """单例模式，同一路径只创建一个实例"""
        abs_path = os.path.abspath(db_path)
        if abs_path not in cls._instances:
            instance = super(SQLiteDocumentStore, cls).__new__(cls)
            cls._instances[abs_path] = instance
        return cls._instances[abs_path]

    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                importance REAL NOT NULL,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # 创建概念表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concepts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建记忆-概念关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_concepts (
                memory_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (memory_id, concept_id),
                FOREIGN KEY (memory_id) REFERENCES memories (id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts (id) ON DELETE CASCADE
            )
        """)

        # 创建记忆-概念关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_concepts(
                memory_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (memory_id, concept_id),
                FOREIGN KEY (memory_id) REFERENCES memories (id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts (id) ON DELETE CASCADE
            )
            """
        )

        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories (memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories (importance)",
            "CREATE INDEX IF NOT EXISTS idx_memory_concepts_memory ON memory_concepts (memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_memory_concepts_concept ON memory_concepts (concept_id)"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        conn.commit()
        print("[OK] SQLite 数据库表和索引创建完成")


    def _get_connection(self):
        """
        获取线程本地连接"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path)
            self.local.connection.row_factory = sqlite3.Row  # 使结果可以按列名访问
        return self.local.connection

    def close(self):
        """关闭数据库连接"""
        if hasattr(self.local, 'connection'):
            self.local.connection.close()
            delattr(self.local, 'connection')
            print("[OK] SQLite 连接已关闭")