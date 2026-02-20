"""
Simple Test Script for Vector Storage Module
============================================
"""

import sys
import os
import tempfile
import shutil

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic ChromaDB functionality"""
    temp_dir = tempfile.mkdtemp(prefix="vector_test_")
    
    try:
        # Import the module
        from core.vector_storage import VectorStorage, CHROMADB_AVAILABLE
        
        print(f"ChromaDB available: {CHROMADB_AVAILABLE}")
        
        if not CHROMADB_AVAILABLE:
            print("SKIP: ChromaDB not available")
            return
        
        # Test initialization
        print("\n1. Testing initialization...")
        vs = VectorStorage(persist_dir=os.path.join(temp_dir, "vector_store"))
        print(f"   - Created VectorStorage with persist_dir: {temp_dir}")
        print(f"   - Collections: {vs.list_collections()}")
        
        # Test adding vectors
        print("\n2. Testing add_vector...")
        doc_id = vs.add_vector(
            content="Python is a great programming language",
            collection_name="knowledge",
            metadata={"tags": ["python", "programming"]}
        )
        print(f"   - Added document with id: {doc_id}")
        
        doc_id2 = vs.add_vector(
            content="Machine learning and AI are transforming technology",
            collection_name="knowledge",
            metadata={"tags": ["ai", "ml"]}
        )
        print(f"   - Added second document with id: {doc_id2}")
        
        # Test search
        print("\n3. Testing search_vector...")
        results = vs.search_vector(
            query="Python programming",
            collection_name="knowledge",
            n_results=5
        )
        print(f"   - Found {len(results)} results")
        for r in results:
            print(f"   - [distance={r.get('distance', 'N/A'):.4f}] {r.get('content', '')[:50]}...")
        
        # Test update
        print("\n4. Testing update_vector...")
        vs.update_vector(
            doc_id=doc_id,
            content="Python is an excellent programming language for AI",
            collection_name="knowledge"
        )
        print("   - Updated document content")
        
        # Test get
        print("\n5. Testing get_vector...")
        doc = vs.get_vector(doc_id)
        if doc:
            print(f"   - Retrieved: {doc.get('content', '')[:50]}...")
        
        # Test delete
        print("\n6. Testing delete_vector...")
        deleted = vs.delete_vector(doc_id2)
        print(f"   - Deleted document: {deleted}")
        
        # Test stats
        print("\n7. Testing collection stats...")
        stats = vs.get_collection_stats(collection_name="knowledge")
        print(f"   - Knowledge collection count: {stats['document_count']}")
        
        # Clean up
        vs.close()
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_basic_functionality()
