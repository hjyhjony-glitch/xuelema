"""
双写引擎
同时写入 SQLite、向量存储和文件存储
"""
import threading
import queue
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import json

# 导入 MemoryType 用于类型验证
import sys
import os
_project_root = os.path.dirname(os.path.dirname(__file__))
_memory_path = os.path.join(_project_root, '.memory')
if _memory_path not in sys.path:
    sys.path.insert(0, _memory_path)
from crud_api import MemoryType


class WriteMode(Enum):
    """写入模式"""
    SYNC = "sync"       # 同步写入（阻塞）
    ASYNC = "async"     # 异步写入（队列）
    BATCH = "batch"     # 批量写入


class DualWriter:
    """
    双写引擎
    
    同时写入多个存储后端：
    1. SQLite - 主存储
    2. 向量存储 - 索引
    3. 文件 - 备份
    """
    
    def __init__(self, mode: WriteMode = WriteMode.SYNC):
        self.mode = mode
        self.queue = queue.Queue() if mode == WriteMode.ASYNC else None
        self._lock = threading.Lock()
        self._workers = []
        self._running = False
        
        # 存储后端配置
        self.backends = {
            "sqlite": True,
            "vector": True,
            "file": True
        }
    
    def configure_backends(self, sqlite: bool = True, vector: bool = True, file: bool = True):
        """配置启用的后端"""
        with self._lock:
            self.backends = {
                "sqlite": sqlite,
                "vector": vector,
                "file": file
            }
    
    def write(
        self,
        operation: str,  # save/delete/update
        data: Dict,
        on_complete: Callable = None
    ):
        """
        写入数据（自动同步到所有后端）
        
        Args:
            operation: 操作类型
            data: 数据
            on_complete: 完成回调
        """
        if self.mode == WriteMode.ASYNC:
            self.queue.put((operation, data, on_complete))
            self._start_worker()
        else:
            self._write_sync(operation, data, on_complete)
    
    def _write_sync(
        self,
        operation: str,
        data: Dict,
        on_complete: Callable = None
    ):
        """同步写入"""
        results = {}
        
        # SQLite
        if self.backends["sqlite"]:
            results["sqlite"] = self._write_sqlite(operation, data)
        
        # 向量存储
        if self.backends["vector"]:
            results["vector"] = self._write_vector(operation, data)
        
        # 文件
        if self.backends["file"]:
            results["file"] = self._write_file(operation, data)
        
        # 回调
        if on_complete:
            on_complete(results)
    
    def _write_sqlite(self, operation: str, data: Dict) -> bool:
        """写入 SQLite"""
        try:
            from memory_system.unified_api import get_unified_memory
            um = get_unified_memory()
            
            if operation == "save":
                memory_type = data.get("memory_type", "custom")
                # 确保是有效的 MemoryType
                try:
                    mem_type_enum = MemoryType(memory_type)
                except ValueError:
                    mem_type_enum = MemoryType.CUSTOM
                
                return bool(um.save(
                    key=data.get("key"),
                    value=data.get("value"),
                    memory_type=mem_type_enum,
                    tags=data.get("tags", []),
                    metadata=data.get("metadata", {}),
                    sync_file=False  # 避免重复写入
                ))
            elif operation == "delete":
                return um.delete(key=data.get("key")) > 0
            
        except Exception as e:
            print(f"SQLite write error: {e}")
            return False
        
        return True
    
    def _write_vector(self, operation: str, data: Dict) -> bool:
        """写入向量存储"""
        try:
            from memory_system.unified_api import get_unified_memory
            um = get_unified_memory()
            
            if operation == "save":
                # 向量存储由 unified_api 自动处理
                pass
            elif operation == "delete":
                # 删除向量
                pass
            
            return True
        except Exception as e:
            print(f"Vector write error: {e}")
            return False
    
    def _write_file(self, operation: str, data: Dict) -> bool:
        """写入文件"""
        try:
            from memory_system.unified_api import get_unified_memory
            um = get_unified_memory()
            
            if operation == "save":
                um._sync_to_file(
                    key=data.get("key"),
                    value=data.get("value"),
                    memory_type=data.get("memory_type", "custom"),
                    tags=data.get("tags", []),
                    metadata=data.get("metadata", {})
                )
            elif operation == "delete":
                um._delete_from_file(data.get("key"))
            
            return True
        except Exception as e:
            print(f"File write error: {e}")
            return False
    
    def _start_worker(self):
        """启动异步工作线程"""
        if not self._running:
            self._running = True
            worker = threading.Thread(target=self._process_queue, daemon=True)
            worker.start()
            self._workers.append(worker)
    
    def _process_queue(self):
        """处理异步队列"""
        while True:
            try:
                operation, data, on_complete = self.queue.get(timeout=1)
                self._write_sync(operation, data, on_complete)
            except queue.Empty:
                if not self._running:
                    break
    
    def stop(self):
        """停止异步工作"""
        self._running = False
        for worker in self._workers:
            worker.join(timeout=1)
        self._workers.clear()
    
    def batch_write(self, items: List[Dict], on_complete: Callable = None):
        """
        批量写入
        
        Args:
            items: 数据列表 [{operation, data}, ...]
            on_complete: 完成回调
        """
        results = []
        for item in items:
            result = self._write_sync(item["operation"], item["data"], None)
            results.append(result)
        
        if on_complete:
            on_complete(results)
        
        return results


# 全局实例
_dual_writer = None

def get_dual_writer(mode: WriteMode = WriteMode.SYNC) -> DualWriter:
    """获取双写引擎实例"""
    global _dual_writer
    if _dual_writer is None:
        _dual_writer = DualWriter(mode)
    return _dual_writer
