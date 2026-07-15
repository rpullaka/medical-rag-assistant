import uuid
from typing import Dict, List, Optional, Tuple

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (Distance, PointStruct, TextIndexParams,
                                       TextIndexType, TokenizerType,
                                       VectorParams)
from sentence_transformers import SentenceTransformer


class MedicalVectorDB:
    """
    Advanced medical document vector database using Qdrant with native hybrid search.
    Implements vector search + BM25 with RRF (Reciprocal Rank Fusion).
    """

    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer(
            "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
        )
        self.collection_name = "medical_knowledge"
        self.vector_size = 384

        # Field boost parameters optimized for medical queries
        self.field_boosts = {
            "question": 1.62,
            "answer": 1.70,
            "medical_department": 1.67,
            "condition_type": 0.97,
            "patient_demographics": 0.64,
            "common_symptoms": 1.75,
            "treatment_or_management": 0.27,
            "severity": 1.85,
        }

    def create_collection(self, recreate: bool = False) -> bool:
        """Create Qdrant collection for medical documents with BM25 text indexing."""
        try:
            if recreate and self.client.collection_exists(self.collection_name):
                self.client.delete_collection(self.collection_name)

            if not self.client.collection_exists(self.collection_name):
                # Create collection with vector and text index configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )

                # Create text index for BM25 search on key fields
                text_index_fields = [
                    "question",
                    "answer",
                    "medical_department",
                    "condition_type",
                    "patient_demographics",
                    "common_symptoms",
                    "treatment_or_management",
                    "severity",
                ]

                for field in text_index_fields:
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field,
                            field_schema=TextIndexParams(
                                type=TextIndexType.TEXT,
                                tokenizer=TokenizerType.WORD,
                                min_token_len=2,
                                max_token_len=20,
                                lowercase=True,
                            ),
                        )
                    except Exception as idx_error:
                        print(
                            f"Warning: Could not create text index for {field}: {idx_error}"
                        )

            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False

    def _prepare_document_text(self, doc: Dict) -> Tuple[str, str, str]:
        """Prepare different text representations for a document."""
        question = doc.get("question", "No question provided")
        answer = doc.get("answer", "No answer provided")

        # Combined text for semantic search
        combined_text = f"{question} {answer}"

        # Full context text for keyword matching
        metadata_parts = []
        for field in [
            "medical_department",
            "condition_type",
            "patient_demographics",
            "common_symptoms",
            "treatment_or_management",
            "severity",
        ]:
            value = doc.get(field, "")
            if value and value != "N/A":
                metadata_parts.append(f"{field.replace('_', ' ')}: {value}")

        full_context = f"{question} {answer} {' '.join(metadata_parts)}"

        return question, combined_text, full_context

    def ingest_documents(self, documents: List[Dict]) -> bool:
        """Ingest medical documents into Qdrant with vector and text indexing."""
        try:
            points = []

            for doc in documents:
                # Ensure proper ID format for Qdrant (UUID or integer)
                original_id = doc.get("id", 0)
                if isinstance(original_id, (int, float)):
                    doc_id = str(uuid.uuid4())  # Generate UUID for Qdrant
                else:
                    doc_id = str(original_id)

                question, combined_text, full_context = self._prepare_document_text(doc)

                # Generate vector embedding
                vector = self.model.encode(combined_text).tolist()

                # Prepare payload with all document fields (keep original ID in payload)
                payload = {
                    "original_id": str(original_id),  # Keep original ID for reference
                    "question": question,
                    "answer": doc.get("answer", ""),
                    "medical_department": doc.get("medical_department", ""),
                    "condition_type": doc.get("condition_type", ""),
                    "patient_demographics": doc.get("patient_demographics", ""),
                    "common_symptoms": doc.get("common_symptoms", ""),
                    "treatment_or_management": doc.get("treatment_or_management", ""),
                    "severity": doc.get("severity", ""),
                    "combined_text": combined_text,
                    "full_context": full_context,
                }

                points.append(PointStruct(id=doc_id, vector=vector, payload=payload))

            # Upload points to Qdrant
            self.client.upsert(collection_name=self.collection_name, points=points)

            print(f"Successfully ingested {len(points)} documents")
            return True

        except Exception as e:
            print(f"Error ingesting documents: {e}")
            return False

    def _create_bm25_query(self, query: str) -> models.Filter:
        """Create BM25 query filter for text search."""
        # Split query into terms
        terms = query.lower().split()

        # Create should clauses for different fields with boosts
        should_clauses = []

        for field, boost in self.field_boosts.items():
            for term in terms:
                should_clauses.append(
                    models.FieldCondition(key=field, match=models.MatchText(text=term))
                )

        return models.Filter(should=should_clauses) if should_clauses else None

    def _apply_domain_scoring(
        self, rrf_scores: Dict[str, float], query: str, all_results: List
    ) -> Dict[str, float]:
        """Apply medical domain-specific scoring enhancements."""
        enhanced_scores = {}
        query_words = set(query.lower().split())

        # Create a mapping from doc_id to payload for easy access
        doc_payloads = {}
        for hit in all_results:
            doc_payloads[hit.id] = hit.payload

        for doc_id, rrf_score in rrf_scores.items():
            if doc_id not in doc_payloads:
                continue

            doc = doc_payloads[doc_id]

            # Base RRF score (ensure it's not zero)
            total_score = max(rrf_score, 0.001)

            # Boost for exact matches in critical fields
            critical_fields = ["question", "common_symptoms", "treatment_or_management"]
            for field in critical_fields:
                field_text = doc.get(field, "").lower()
                if any(word in field_text for word in query_words):
                    total_score *= 1.2

            # Boost for medical department relevance
            if any(
                word in doc.get("medical_department", "").lower()
                for word in query_words
            ):
                total_score *= 1.15

            # Severity-based scoring adjustment
            severity = doc.get("severity", "").lower()
            severity_multipliers = {
                "life-threatening": 1.3,
                "severe": 1.2,
                "moderate": 1.1,
                "mild": 1.0,
            }
            total_score *= severity_multipliers.get(severity, 1.0)

            enhanced_scores[doc_id] = total_score

        return enhanced_scores

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Perform hybrid search using Qdrant's built-in capabilities with RRF fusion."""
        try:
            query_vector = self.model.encode(query).tolist()

            # Perform vector search
            vector_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=20,  # Get more results for RRF
                with_payload=True,
                with_vectors=False,
            )

            # Perform BM25 text search using query filter
            bm25_filter = self._create_bm25_query(query)
            bm25_results = []

            if bm25_filter:
                bm25_results = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=bm25_filter,
                    limit=20,
                    with_payload=True,
                    with_vectors=False,
                )[
                    0
                ]  # scroll returns (points, next_page_offset)

            # Apply RRF fusion
            rrf_scores = {}
            k = 60  # RRF parameter

            # Process vector results
            for rank, hit in enumerate(vector_results):
                doc_id = hit.id
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (k + rank + 1))

            # Process BM25 results
            for rank, hit in enumerate(bm25_results):
                doc_id = hit.id
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (k + rank + 1))

            # Enhanced scoring with medical domain knowledge
            enhanced_scores = self._apply_domain_scoring(
                rrf_scores, query, vector_results + bm25_results
            )

            # Sort and return top results
            sorted_results = sorted(
                enhanced_scores.items(), key=lambda x: x[1], reverse=True
            )

            final_results = []
            seen_docs = set()

            for doc_id, score in sorted_results[:top_k]:
                # Find the document in results
                doc = None
                for hit in vector_results + bm25_results:
                    if hit.id == doc_id:
                        doc = hit.payload
                        break

                if doc and doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    result_doc = doc.copy()
                    result_doc["id"] = result_doc.get("original_id", doc_id)
                    result_doc["fusion_score"] = score

                    # Remove internal fields
                    for field in ["combined_text", "full_context", "original_id"]:
                        result_doc.pop(field, None)

                    final_results.append(result_doc)

            return final_results

        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return []

    def get_collection_info(self) -> Optional[Dict]:
        """Get information about the collection."""
        try:
            if self.client.collection_exists(self.collection_name):
                info = self.client.get_collection(self.collection_name)
                return {
                    "name": self.collection_name,
                    "vectors_count": info.vectors_count,
                    "status": info.status,
                }
        except Exception as e:
            print(f"Error getting collection info: {e}")
        return None


def load_data_and_create_collection(
    data_path: str = "../data/medical_qa_metadata_sample.csv",
    host: str = "localhost",
    port: int = 6333,
) -> MedicalVectorDB:
    """Load medical data and create Qdrant collection."""
    # Initialize vector database
    vector_db = MedicalVectorDB(host=host, port=port)

    # Create collection
    vector_db.create_collection(recreate=True)

    # Load data
    df = pd.read_csv(data_path)
    documents = df.to_dict(orient="records")

    # Ingest documents
    vector_db.ingest_documents(documents)

    return vector_db
