"""
简易向量存储模块 (纯 Python + NumPy)
兼容 Python 3.14

注意：当前使用字符频率哈希作为伪向量，生产环境建议替换为真正的 embedding 模型（如 sentence-transformers）。
"""
import numpy as np
from typing import List, Dict, Optional
import json
import os
from datetime import datetime

class VectorStorage:
    """基于 NumPy 的简易向量存储"""
    
    def __init__(self, persist_dir: str = ".memory/vector_db"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # 内存存储
        self.collections: Dict[str, Dict] = {
            "memories": {"ids": [], "documents": [], "metadatas": [], "vectors": []},
            "conversations": {"ids": [], "documents": [], "metadatas": [], "vectors": []},
            "knowledge": {"ids": [], "documents": [], "metadatas": [], "vectors": []}
        }
        
        # 简单的文本哈希作为伪向量 (实际使用应替换为 embedding)
        self._load()
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """简单文本哈希转向量 (占位符)"""
        # 使用字符频率作为简单特征
        text = text.lower()
        vec = np.zeros(256)
        for i, char in enumerate(text[:256]):
            vec[ord(char) % 256] += 1
        # L2 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
    
    def add(self, collection: str, doc_id: str, document: str, metadata: dict = None):
        """添加向量"""
        if collection not in self.collections:
            self.collections[collection] = {"ids": [], "documents": [], "metadatas": [], "vectors": []}
        
        coll = self.collections[collection]
        coll["ids"].append(doc_id)
        coll["documents"].append(document)
        coll["metadatas"].append(metadata or {})
        coll["vectors"].append(self._text_to_vector(document))
        
        self._save()
    
    def search(self, collection: str, query: str, n_results: int = 5):
        """
        搜索向量 (L2 距离)
        
        Args:
            collection: 集合名称
            query: 查询文本
            n_results: 返回结果数量
        
        Returns:
            dict: 包含 ids, documents, metadatas, distances
        """
        if collection not in self.collections:
            return None
        
        coll = self.collections[collection]
        if not coll["vectors"]:
            return None
        
        query_vec = self._text_to_vector(query)
        vectors = np.array(coll["vectors"])
        
        # 计算 L2 距离
        distances = np.linalg.norm(vectors - query_vec, axis=1)
        
        # 获取 top n (距离越小越相似)
        top_indices = np.argsort(distances)[:n_results]
        
        results = {
            "ids": [coll["ids"][i] for i in top_indices],
            "documents": [coll["documents"][i] for i in top_indices],
            "metadatas": [coll["metadatas"][i] for i in top_indices],
            "distances": [float(distances[i]) for i in top_indices]
        }
        return results
    
    def delete(self, collection: str, doc_id: str):
        """删除向量"""
        if collection not in self.collections:
            return
        
        coll = self.collections[collection]
        if doc_id in coll["ids"]:
            idx = coll["ids"].index(doc_id)
            coll["ids"].pop(idx)
            coll["documents"].pop(idx)
            coll["metadatas"].pop(idx)
            coll["vectors"].pop(idx)
            self._save()
    
    def _save(self):
        """保存到磁盘"""
        data = {}
        for name, coll in self.collections.items():
            data[name] = {
                "ids": coll["ids"],
                "documents": coll["documents"],
                "metadatas": coll["metadatas"]
            }
        with open(os.path.join(self.persist_dir, "vectors.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """从磁盘加载"""
        path = os.path.join(self.persist_dir, "vectors.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for name, coll in data.items():
                    if name in self.collections:
                        self.collections[name]["ids"] = coll.get("ids", [])
                        self.collections[name]["documents"] = coll.get("documents", [])
                        self.collections[name]["metadatas"] = coll.get("metadatas", [])
                        self.collections[name]["vectors"] = [
                            self._text_to_vector(doc) for doc in self.collections[name]["documents"]
                        ]
            except Exception:
                pass

# 全局实例
vector_db = VectorStorage()

# 便捷函数
def add_vector(collection: str, doc_id: str, document: str, metadata: dict = None):
    """添加向量到指定集合"""
    return vector_db.add(collection, doc_id, document, metadata)

def search_vector(collection: str, query: str, n_results: int = 5):
    """
    在指定集合中搜索向量
    
    Args:
        collection: 集合名称
        query: 查询文本
        n_results: 返回结果数量
    
    Returns:
        dict: 包含 ids, documents, metadatas, distances
    """
    return vector_db.search(collection, query, n_results)

def delete_vector(collection: str, doc_id: str):
    """从指定集合删除向量"""
    return vector_db.delete(collection, doc_id)
