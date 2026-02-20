"""
记忆系统集成模块
统一 SQLite、向量存储和文件存储
"""

from .unified_api import (
    UnifiedMemory,
    get_unified_memory,
    save_to_memory,
    load_from_memory,
    search_memory_v2
)

from .dual_writer import (
    DualWriter,
    WriteMode,
    get_dual_writer
)

from .file_sync import (
    FileSync,
    get_file_sync
)

from .openclaw_integration import (
    get_memory_manager,
    memory_search,
    memory_get,
    remember,
    recall,
    init_memory_system
)

__all__ = [
    # Unified API
    "UnifiedMemory",
    "get_unified_memory",
    "save_to_memory",
    "load_from_memory",
    "search_memory_v2",
    
    # Dual Writer
    "DualWriter",
    "WriteMode",
    "get_dual_writer",
    
    # File Sync
    "FileSync",
    "get_file_sync",
    
    # OpenClaw Integration
    "get_memory_manager",
    "memory_search",
    "memory_get",
    "remember",
    "recall",
    "init_memory_system"
]
