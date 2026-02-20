"""
注意：当前使用字符频率哈希作为伪向量，生产环境建议替换为真正的 embedding 模型（如 sentence-transformers）。
"""

"""
ChromaDB Vector Storage Module
=============================
向量存储模块，提供向量的添加、搜索、更新、删除功能。

功能:
- 初始化 ChromaDB 集合
- 添加向量 (add_vector)
- 搜索向量 (search_vector)
- 删除向量 (delete_vector)
- 更新向量 (update_vector)

依赖:
- chromadb>=0.4.0

Author: RUNBOT-DEV（笑天）
Version: 1.0.0
Date: 2026-02-20
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import uuid
import threading

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None  # type: ignore


class VectorStorageError(Exception):
    """向量存储基础异常类"""
    pass


class CollectionNotFoundError(VectorStorageError):
    """集合不存在异常"""
    pass


class DocumentNotFoundError(VectorStorageError):
    """文档不存在异常"""
    pass


class EmbeddingError(VectorStorageError):
    """向量生成异常"""
    pass


class VectorStorage:
    """
    ChromaDB 向量存储管理器
    
    提供向量的持久化存储和语义搜索功能。
    
    Attributes:
        persist_dir: 持久化存储目录
        collections: 集合字典
        embedding_function: 文本向量化函数
        lock: 线程锁（保证并发安全）
    """
    
    # 默认集合名称
    COLLECTION_CONVERSATIONS = "conversations"
    COLLECTION_GOALS = "goals"
    COLLECTION_KNOWLEDGE = "knowledge"
    
    def __init__(
        self,
        persist_dir: str = "./.memory/vector_store",
        embedding_function: Optional[Any] = None,
        chroma_server_host: Optional[str] = None,
        chroma_server_http_port: Optional[int] = None
    ) -> None:
        """
        初始化向量存储
        
        Args:
            persist_dir: 持久化存储目录路径
            embedding_function: 自定义向量化函数（可选）
                接受文本字符串，返回向量列表
            chroma_server_host: ChromaDB 服务器地址（可选）
                如果指定则使用远程连接
            chroma_server_http_port: ChromaDB 服务器端口（可选）
        
        Raises:
            VectorStorageError: ChromaDB 不可用时抛出
        """
        if not CHROMADB_AVAILABLE:
            raise VectorStorageError(
                "ChromaDB is not installed. "
                "Please install it with: pip install chromadb>=0.4.0"
            )
        
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_function = embedding_function
        self._collections: Dict[str, Any] = {}
        self._lock = threading.RLock()
        
        # 初始化客户端
        if chroma_server_host and chroma_server_http_port:
            # 远程模式
            self._client = chromadb.HttpClient(
                host=chroma_server_host,
                port=chroma_server_http_port
            )
        else:
            # 本地持久化模式
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
        
        # 初始化默认集合
        self._init_collections()
    
    def _init_collections(self) -> None:
        """初始化默认集合"""
        default_collections = [
            self.COLLECTION_CONVERSATIONS,
            self.COLLECTION_GOALS,
            self.COLLECTION_KNOWLEDGE
        ]
        
        for collection_name in default_collections:
            try:
                self._get_or_create_collection(collection_name)
            except VectorStorageError:
                # 忽略初始化错误，在实际使用时处理
                pass
    
    def _get_or_create_collection(self, name: str) -> Any:
        """
        获取或创建集合
        
        Args:
            name: 集合名称
            
        Returns:
            ChromaDB 集合对象
            
        Raises:
            VectorStorageError: 集合创建失败时抛出
        """
        with self._lock:
            if name in self._collections:
                return self._collections[name]
            
            try:
                # 尝试获取已存在的集合
                collection = self._client.get_collection(name=name)
            except Exception:
                # 集合不存在，创建新集合
                try:
                    collection = self._client.create_collection(
                        name=name,
                        metadata={"description": f"Collection for {name}"}
                    )
                except Exception as e:
                    raise VectorStorageError(
                        f"Failed to create collection '{name}': {e}"
                    )
            
            self._collections[name] = collection
            return collection
    
    def _generate_id(self) -> str:
        """生成唯一文档 ID"""
        return f"doc_{uuid.uuid4().hex[:16]}"
    
    def _validate_collection(self, collection_name: Optional[str]) -> str:
        """
        验证并返回集合名称
        
        Args:
            collection_name: 集合名称（可选）
            
        Returns:
            验证后的集合名称
            
        Raises:
            CollectionNotFoundError: 集合不存在时抛出
        """
        if collection_name is None:
            collection_name = self.COLLECTION_KNOWLEDGE
        
        if collection_name not in self._collections:
            try:
                self._get_or_create_collection(collection_name)
            except VectorStorageError as e:
                raise CollectionNotFoundError(
                    f"Collection '{collection_name}' not found: {e}"
                )
        
        return collection_name
    
    def add_vector(
        self,
        content: str,
        collection_name: Optional[str] = None,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        添加向量到存储
        
        将文本内容向量化并存储到指定集合中。
        
        Args:
            content: 要向化的文本内容
            collection_name: 集合名称（默认: knowledge）
            doc_id: 文档 ID（可选，默认自动生成）
            metadata: 元数据字典（可选）
            
        Returns:
            str: 文档 ID
            
        Raises:
            VectorStorageError: 添加失败时抛出
            CollectionNotFoundError: 集合不存在时抛出
        """
        collection_name = self._validate_collection(collection_name)
        doc_id = doc_id or self._generate_id()
        metadata = metadata or {}
        
        # 添加时间戳元数据
        from datetime import datetime
        metadata["created_at"] = datetime.now().isoformat()
        metadata["updated_at"] = datetime.now().isoformat()
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                # 使用 embedding function 或默认处理
                if self.embedding_function:
                    embeddings = self.embedding_function([content])
                else:
                    # ChromaDB 会自动生成 embedding
                    embeddings = None
                
                # 添加到集合
                collection.add(
                    documents=[content],
                    ids=[doc_id],
                    metadatas=[metadata],
                    embeddings=embeddings
                )
                
                return doc_id
                
            except Exception as e:
                raise VectorStorageError(
                    f"Failed to add vector to collection '{collection_name}': {e}"
                )
    
    def add_vectors(
        self,
        contents: List[str],
        collection_name: Optional[str] = None,
        doc_ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        批量添加向量
        
        Args:
            contents: 文本内容列表
            collection_name: 集合名称
            doc_ids: 文档 ID 列表（可选，自动生成）
            metadatas: 元数据列表（可选）
            
        Returns:
            List[str]: 文档 ID 列表
            
        Raises:
            VectorStorageError: 添加失败时抛出
        """
        collection_name = self._validate_collection(collection_name)
        
        # 生成 ID 列表
        if doc_ids is None:
            doc_ids = [self._generate_id() for _ in contents]
        elif len(doc_ids) != len(contents):
            raise VectorStorageError(
                f"Length mismatch: contents ({len(contents)}) != "
                f"doc_ids ({len(doc_ids)})"
            )
        
        # 补齐元数据
        if metadatas is None:
            metadatas = [{} for _ in contents]
        
        from datetime import datetime
        for i, meta in enumerate(metadatas):
            if not isinstance(meta, dict):
                metadatas[i] = {}
            metadatas[i]["created_at"] = datetime.now().isoformat()
            metadatas[i]["updated_at"] = datetime.now().isoformat()
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                if self.embedding_function:
                    embeddings = self.embedding_function(contents)
                else:
                    embeddings = None
                
                collection.add(
                    documents=contents,
                    ids=doc_ids,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
                
                return doc_ids
                
            except Exception as e:
                raise VectorStorageError(
                    f"Failed to add vectors to collection '{collection_name}': {e}"
                )
    
    def search_vector(
        self,
        query: str,
        collection_name: Optional[str] = None,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索向量
        
        在指定集合中搜索与查询最相似的向量。
        
        Args:
            query: 查询文本
            collection_name: 集合名称（可选，默认搜索所有集合）
            n_results: 返回结果数量（默认: 5）
            where: 元数据过滤条件（可选）
                示例: {"tags": {"$in": ["important"]}}
            where_document: 文档内容过滤条件（可选）
                示例: {"$contains": "python"}
            
        Returns:
            List[Dict]: 搜索结果列表
                每个结果包含: id, content, metadata, distance/score
            
        Raises:
            VectorStorageError: 搜索失败时抛出
        """
        results: List[Dict[str, Any]] = []
        
        if collection_name:
            # 搜索指定集合
            collection_name = self._validate_collection(collection_name)
            results = self._search_collection(
                collection_name, query, n_results, where, where_document
            )
        else:
            # 搜索所有集合
            for name in self._collections.keys():
                collection_results = self._search_collection(
                    name, query, n_results, where, where_document
                )
                for result in collection_results:
                    result["collection"] = name
                results.extend(collection_results)
            
            # 合并结果并按距离排序
            results.sort(key=lambda x: x.get("distance", float("inf")))
            results = results[:n_results]
        
        return results
    
    def _search_collection(
        self,
        collection_name: str,
        query: str,
        n_results: int,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        在指定集合中搜索
        
        Args:
            collection_name: 集合名称
            query: 查询文本
            n_results: 返回数量
            where: 元数据过滤
            where_document: 文档过滤
            
        Returns:
            List[Dict]: 搜索结果
        """
        with self._lock:
            try:
                collection = self._get_or_create_collection(collection_name)
                
                # 构建查询参数
                query_params = {
                    "query_texts": [query],
                    "n_results": n_results,
                    "where": where,
                    "where_document": where_document
                }
                
                # 过滤空参数
                query_params = {k: v for k, v in query_params.items() if v is not None}
                
                raw_results = collection.query(**query_params)
                
                # 解析结果
                parsed_results: List[Dict[str, Any]] = []
                
                if raw_results.get("ids") and raw_results["ids"][0]:
                    ids = raw_results["ids"][0]
                    documents = raw_results.get("documents", [[]])[0]
                    metadatas = raw_results.get("metadatas", [[]])[0]
                    distances = raw_results.get("distances", [[]])[0]
                    
                    for i, doc_id in enumerate(ids):
                        result = {
                            "id": doc_id,
                            "content": documents[i] if i < len(documents) else "",
                            "metadata": metadatas[i] if i < len(metadatas) else {},
                            "distance": distances[i] if i < len(distances) else 0.0,
                            "collection": collection_name
                        }
                        parsed_results.append(result)
                
                return parsed_results
                
            except Exception as e:
                raise VectorStorageError(
                    f"Search failed in collection '{collection_name}': {e}"
                )
    
    def search_similar(
        self,
        query: str,
        doc_id: str,
        collection_name: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索与指定文档相似的向量
        
        Args:
            query: 查询文本（用于定位参考向量）
            doc_id: 参考文档 ID
            collection_name: 集合名称
            n_results: 返回数量（包含参考文档）
            
        Returns:
            List[Dict]: 相似结果列表
            
        Raises:
            DocumentNotFoundError: 文档不存在时抛出
        """
        collection_name = self._validate_collection(collection_name)
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                # 获取参考文档
                ref_doc = collection.get(ids=[doc_id])
                if not ref_doc["documents"]:
                    raise DocumentNotFoundError(
                        f"Document '{doc_id}' not found in collection '{collection_name}'"
                    )
                
                # 使用参考文档的 embedding 搜索相似文档
                raw_results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where_document={"$not_contains": "PLACEHOLDER"}
                )
                
                # 解析结果（排除参考文档本身）
                results: List[Dict[str, Any]] = []
                for i, doc_id_result in enumerate(raw_results["ids"][0]):
                    if doc_id_result != doc_id:
                        results.append({
                            "id": doc_id_result,
                            "content": raw_results["documents"][0][i],
                            "metadata": raw_results["metadatas"][0][i],
                            "distance": raw_results["distances"][0][i]
                        })
                
                return results
                
            except DocumentNotFoundError:
                raise
            except Exception as e:
                raise VectorStorageError(
                    f"Similar search failed: {e}"
                )
    
    def delete_vector(
        self,
        doc_id: str,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        删除向量
        
        从指定集合中删除指定 ID 的向量。
        
        Args:
            doc_id: 要删除的文档 ID
            collection_name: 集合名称（可选，默认在所有集合中查找）
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            DocumentNotFoundError: 文档不存在时抛出（可选检查）
        """
        with self._lock:
            if collection_name:
                # 删除指定集合中的文档
                collection_name = self._validate_collection(collection_name)
                collection = self._get_or_create_collection(collection_name)
                
                try:
                    collection.delete(ids=[doc_id])
                    return True
                except Exception:
                    # 文档可能不存在，视为成功
                    return False
            else:
                # 在所有集合中查找并删除
                deleted = False
                for name in list(self._collections.keys()):
                    try:
                        collection = self._get_or_create_collection(name)
                        collection.delete(ids=[doc_id])
                        deleted = True
                    except Exception:
                        pass
                return deleted
    
    def delete_vectors(
        self,
        doc_ids: List[str],
        collection_name: Optional[str] = None
    ) -> int:
        """
        批量删除向量
        
        Args:
            doc_ids: 要删除的文档 ID 列表
            collection_name: 集合名称
            
        Returns:
            int: 实际删除的文档数量
        """
        with self._lock:
            if collection_name:
                collection_name = self._validate_collection(collection_name)
                collection = self._get_or_create_collection(collection_name)
                
                try:
                    collection.delete(ids=doc_ids)
                    return len(doc_ids)
                except Exception:
                    return 0
            else:
                # 在所有集合中删除
                total_deleted = 0
                for name in self._collections.keys():
                    collection = self._get_or_create_collection(name)
                    deleted_in_collection = 0
                    
                    for doc_id in doc_ids:
                        try:
                            collection.delete(ids=[doc_id])
                            deleted_in_collection += 1
                        except Exception:
                            pass
                    
                    total_deleted += deleted_in_collection
                
                return total_deleted
    
    def update_vector(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        更新向量
        
        更新指定文档的内容和/或元数据。
        
        Args:
            doc_id: 文档 ID
            content: 新内容（可选）
            metadata: 新元数据（可选，将合并）
            collection_name: 集合名称
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            DocumentNotFoundError: 文档不存在时抛出
        """
        collection_name = self._validate_collection(collection_name)
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                # 获取现有数据
                existing = collection.get(ids=[doc_id])
                if not existing["documents"]:
                    raise DocumentNotFoundError(
                        f"Document '{doc_id}' not found in collection '{collection_name}'"
                    )
                
                # 准备更新数据
                new_content = content if content is not None else existing["documents"][0]
                new_metadata = existing["metadatas"][0] if existing["metadatas"] else {}
                
                if metadata:
                    new_metadata.update(metadata)
                
                # 更新时间戳
                from datetime import datetime
                new_metadata["updated_at"] = datetime.now().isoformat()
                
                # 删除旧记录
                collection.delete(ids=[doc_id])
                
                # 添加新记录
                collection.add(
                    documents=[new_content],
                    ids=[doc_id],
                    metadatas=[new_metadata]
                )
                
                return True
                
            except DocumentNotFoundError:
                raise
            except Exception as e:
                raise VectorStorageError(
                    f"Failed to update vector '{doc_id}': {e}"
                )
    
    def upsert_vector(
        self,
        doc_id: str,
        content: str,
        collection_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        插入或更新向量
        
        如果文档存在则更新，不存在则插入。
        
        Args:
            doc_id: 文档 ID
            content: 文档内容
            collection_name: 集合名称
            metadata: 元数据
            
        Returns:
            bool: 是否操作成功
        """
        collection_name = self._validate_collection(collection_name)
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                # 检查文档是否存在
                existing = collection.get(ids=[doc_id])
                doc_exists = bool(existing["documents"])
                
                if doc_exists:
                    # 更新
                    new_metadata = existing["metadatas"][0] if existing["metadatas"] else {}
                    if metadata:
                        new_metadata.update(metadata)
                    
                    from datetime import datetime
                    new_metadata["updated_at"] = datetime.now().isoformat()
                    
                    collection.delete(ids=[doc_id])
                    collection.add(
                        documents=[content],
                        ids=[doc_id],
                        metadatas=[new_metadata]
                    )
                else:
                    # 插入
                    self.add_vector(
                        content=content,
                        doc_id=doc_id,
                        metadata=metadata,
                        collection_name=collection_name
                    )
                
                return True
                
            except Exception as e:
                raise VectorStorageError(
                    f"Failed to upsert vector '{doc_id}': {e}"
                )
    
    def get_vector(
        self,
        doc_id: str,
        collection_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取向量
        
        获取指定文档的内容和元数据。
        
        Args:
            doc_id: 文档 ID
            collection_name: 集合名称
            
        Returns:
            Optional[Dict]: 文档数据，不存在返回 None
        """
        collection_name = self._validate_collection(collection_name)
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                result = collection.get(ids=[doc_id])
                
                if result["documents"]:
                    return {
                        "id": doc_id,
                        "content": result["documents"][0],
                        "metadata": result["metadatas"][0] if result["metadatas"] else {},
                        "collection": collection_name
                    }
                return None
                
            except Exception:
                return None
    
    def get_collection_stats(
        self,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Args:
            collection_name: 集合名称（可选）
            
        Returns:
            Dict: 统计信息
        """
        if collection_name:
            collection_name = self._validate_collection(collection_name)
            collection = self._get_or_create_collection(collection_name)
            
            count = collection.count()
            
            return {
                "collection": collection_name,
                "document_count": count
            }
        else:
            # 所有集合的统计
            stats = {}
            for name in self._collections.keys():
                try:
                    collection = self._get_or_create_collection(name)
                    stats[name] = collection.count()
                except Exception:
                    stats[name] = 0
            
            return stats
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            List[str]: 集合名称列表
        """
        return list(self._collections.keys())
    
    def clear_collection(self, collection_name: str) -> int:
        """
        清空集合
        
        删除集合中的所有文档。
        
        Args:
            collection_name: 集合名称
            
        Returns:
            int: 删除的文档数量
            
        Raises:
            CollectionNotFoundError: 集合不存在时抛出
        """
        collection_name = self._validate_collection(collection_name)
        
        with self._lock:
            collection = self._get_or_create_collection(collection_name)
            
            try:
                # 获取所有文档 ID
                all_docs = collection.get()
                count = len(all_docs["ids"])
                
                if count > 0:
                    collection.delete(ids=all_docs["ids"])
                
                return count
                
            except Exception as e:
                raise VectorStorageError(
                    f"Failed to clear collection '{collection_name}': {e}"
                )
    
    def close(self) -> None:
        """
        关闭存储连接
        """
        with self._lock:
            self._collections.clear()
            # ChromaDB 客户端不需要显式关闭
