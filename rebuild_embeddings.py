#!/usr/bin/env python3
"""
Rebuild RAG Embeddings Script

This script regenerates the embeddings.json file from functions.txt.
Run this after adding or modifying functions in the knowledge base.

Usage:
    python rebuild_embeddings.py [--force]

Options:
    --force    Force rebuild even if embeddings are up-to-date
"""

import os
import sys
from pathlib import Path


def rebuild_embeddings(force: bool = False):
    """
    Rebuild the embeddings from the knowledge base.
    
    Args:
        force: If True, rebuild even if embeddings are up-to-date
    """
    # Import here to ensure we're in the right directory
    sys.path.insert(0, str(Path(__file__).parent))
    from partA.rag_system import InMemoryRAG
    
    print("=" * 70)
    print("🔄 Rebuilding RAG Embeddings")
    print("=" * 70)
    
    kb_path = "partA/knowledge_base/functions.txt"
    emb_path = "partA/knowledge_base/embeddings.json"
    
    # Check if knowledge base exists
    if not os.path.exists(kb_path):
        print(f"❌ Error: Knowledge base not found at {kb_path}")
        print(f"   Please create the file first.")
        return False
    
    # Show knowledge base info
    with open(kb_path, 'r') as f:
        content = f.read()
        function_count = content.count('---')
        
    print(f"\n📚 Knowledge Base: {kb_path}")
    print(f"   Functions: ~{function_count}")
    print(f"   Size: {len(content)} characters")
    
    # Check if embeddings exist
    if os.path.exists(emb_path) and not force:
        print(f"\n⚠️  Embeddings file exists: {emb_path}")
        print(f"   The system will check if it needs updating...")
    elif force:
        print(f"\n🔨 Force mode: Will rebuild embeddings regardless")
        # Delete existing embeddings to force rebuild
        if os.path.exists(emb_path):
            os.remove(emb_path)
            print(f"   Deleted existing embeddings")
    
    try:
        print(f"\n⏳ Initializing RAG system...")
        rag = InMemoryRAG(kb_path, emb_path)
        
        print(f"📖 Loading knowledge base...")
        rag.load_knowledge_base()
        
        print(f"🔢 Generating embeddings...")
        rag.generate_and_save_embeddings()
        
        print("\n" + "=" * 70)
        print("✅ Embeddings rebuilt successfully!")
        print("=" * 70)
        
        # Show summary
        print(f"\n📊 Summary:")
        print(f"   Chunks indexed: {len(rag.chunks)}")
        print(f"   Embedding dimensions: {rag.embeddings.shape[1] if rag.embeddings is not None else 0}")
        print(f"   Model: {rag.embedding_model}")
        print(f"   Output file: {emb_path}")
        
        print(f"\n✨ The updated embeddings will be used on next application run.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error rebuilding embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    args = sys.argv[1:]
    
    # Show help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    # Check for force flag
    force = "--force" in args
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Rebuild embeddings
    success = rebuild_embeddings(force)
    
    if success:
        print("\n" + "=" * 70)
        print("💡 Next steps:")
        print("   1. Your changes are saved in embeddings.json")
        print("   2. Restart the application to use the new embeddings")
        print("   3. The RAG system will use your updated knowledge base")
        print("=" * 70)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
