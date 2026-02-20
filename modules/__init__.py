# Persistent Memory System - Core Module
# ======================================

from .sqlite_storage import SQLiteStorage, create_storage

__version__ = "1.0.0"
__all__ = ["SQLiteStorage", "create_storage"]
