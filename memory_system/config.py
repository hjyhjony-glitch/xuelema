"""
记忆系统配置
"""
import os

# 数据库路径配置
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '.memory/_index/memory.db')
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), '.memory/.memory/vector_db')

# 存储配置
STORAGE_CONFIG = {
    "sqlite": {
        "enabled": True,
        "path": DATABASE_PATH,
        "wal_mode": True
    },
    "vector": {
        "enabled": True,
        "path": VECTOR_DB_PATH,
        "model": "numpy"  # 占位符，实际使用应替换为真正的 embedding
    },
    "file": {
        "enabled": True,
        "path": "memory",
        "format": "markdown"
    }
}

# 写入配置
WRITE_CONFIG = {
    "mode": "sync",  # sync/async/batch
    "retry_count": 3,
    "retry_delay": 1  # 秒
}

# 标签配置
TAG_CONFIG = {
    "max_tags": 10,
    "reserved_tags": ["system", "memory", "migrated", "important"],
    "auto_generate": True
}

# 同步配置
SYNC_CONFIG = {
    "auto_sync": True,
    "sync_interval": 3600,  # 秒
    "backup_on_close": True
}
