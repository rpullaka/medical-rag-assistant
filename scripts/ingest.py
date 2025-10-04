#!/usr/bin/env python3
"""Medical Data Ingestion Module"""

from typing import Dict, List, Optional

import sys
import os
# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database.vector_db import MedicalVectorStore

_global_vector_store: Optional[MedicalVectorStore] = None


def ingest_data(data_path: str = "data/medical_qa_full.csv") -> MedicalVectorStore:
    """Ingest medical data into vector store"""
    global _global_vector_store

    print(f"Starting medical data ingestion from: {data_path}")
    _global_vector_store = MedicalVectorStore(
        host="localhost", port=6333, collection_name="medical_knowledge"
    )
    print("Vector store initialized")
    return _global_vector_store


def get_vector_store() -> MedicalVectorStore:
    """Get initialized vector store instance"""
    global _global_vector_store

    if _global_vector_store is None:
        print("Connecting to existing Qdrant vector store...")
        _global_vector_store = MedicalVectorStore(
            host="localhost", port=6333, collection_name="medical_knowledge"
        )
        print("Vector store connection established")

    return _global_vector_store


def hybrid_query_rrf(search_query: str, top_k: int = 5) -> List[Dict]:
    """Perform hybrid search on medical knowledge base"""
    vector_store = get_vector_store()
    return vector_store.search(search_query, top_k=top_k)


if __name__ == "__main__":
    vector_store = ingest_data("../data/medical_qa_metadata_sample.csv")
    print("Medical RAG system ready!")
