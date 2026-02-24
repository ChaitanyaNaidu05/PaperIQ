import logging
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import numpy as np
    from transformer_analyzer import get_transformer_model, TRANSFORMERS_AVAILABLE
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available for semantic search")


@dataclass
class SearchDocument:
    doc_id: str
    filename: str
    content: str
    embedding: Optional[np.ndarray] = None
    metadata: Optional[Dict] = None


class SemanticSearchIndex:
    def __init__(self, index_file: str = "search_index.json"):
        self.index_file = index_file
        self.documents: Dict[str, SearchDocument] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self._model = None
        self._load_index()

    def _get_model(self):
        if self._model is None and TRANSFORMERS_AVAILABLE:
            self._model = get_transformer_model()
        return self._model

    def _load_index(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r") as f:
                    data = json.load(f)
                for doc_id, doc_data in data.get("documents", {}).items():
                    self.documents[doc_id] = SearchDocument(
                        doc_id=doc_id,
                        filename=doc_data.get("filename", ""),
                        content=doc_data.get("content", ""),
                        metadata=doc_data.get("metadata")
                    )
                self.embeddings = data.get("embeddings", {})
                logger.info(f"Loaded search index with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading search index: {e}")

    def _save_index(self):
        try:
            data = {
                "documents": {
                    doc_id: {
                        "filename": doc.filename,
                        "content": doc.content[:10000],
                        "metadata": doc.metadata
                    }
                    for doc_id, doc in self.documents.items()
                },
                "embeddings": self.embeddings
            }
            with open(self.index_file, "w") as f:
                json.dump(data, f)
            logger.info(f"Saved search index with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error saving search index: {e}")

    def add_document(
        self,
        doc_id: str,
        filename: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        model = self._get_model()
        
        embedding = None
        if model is not None:
            try:
                emb = model.encode(
                    content[:5000],
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                embedding = emb
                self.embeddings[doc_id] = embedding.tolist()
            except Exception as e:
                logger.error(f"Error creating embedding: {e}")
        
        self.documents[doc_id] = SearchDocument(
            doc_id=doc_id,
            filename=filename,
            content=content,
            embedding=embedding,
            metadata=metadata
        )
        
        self._save_index()
        logger.info(f"Added document to search index: {doc_id}")

    def remove_document(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]
        if doc_id in self.embeddings:
            del self.embeddings[doc_id]
        self._save_index()

    def search(
        self,
        query: str,
        top_k: int = 10,
        use_semantic: bool = True
    ) -> List[Tuple[str, float, str]]:
        results = []
        
        if use_semantic and TRANSFORMERS_AVAILABLE:
            results = self._semantic_search(query, top_k)
        else:
            results = self._keyword_search(query, top_k)
        
        return results

    def _semantic_search(
        self,
        query: str,
        top_k: int
    ) -> List[Tuple[str, float, str]]:
        model = self._get_model()
        if model is None or not self.embeddings:
            return self._keyword_search(query, top_k)
        
        try:
            query_embedding = model.encode(
                query,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            scores = []
            for doc_id, doc_emb_list in self.embeddings.items():
                doc_emb = np.array(doc_emb_list)
                similarity = np.dot(query_embedding, doc_emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)
                )
                scores.append((doc_id, float(similarity)))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for doc_id, score in scores[:top_k]:
                doc = self.documents.get(doc_id)
                if doc:
                    snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                    results.append((doc_id, score, snippet))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self._keyword_search(query, top_k)

    def _keyword_search(
        self,
        query: str,
        top_k: int
    ) -> List[Tuple[str, float, str]]:
        query_words = set(query.lower().split())
        
        scores = []
        for doc_id, doc in self.documents.items():
            doc_words = set(doc.content.lower().split())
            intersection = len(query_words & doc_words)
            union = len(query_words | doc_words)
            score = intersection / union if union > 0 else 0
            scores.append((doc_id, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in scores[:top_k]:
            doc = self.documents.get(doc_id)
            if doc:
                snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                results.append((doc_id, score, snippet))
        
        return results

    def get_all_documents(self) -> List[Dict]:
        return [
            {
                "doc_id": doc_id,
                "filename": doc.filename,
                "metadata": doc.metadata
            }
            for doc_id, doc in self.documents.items()
        ]

    def clear_index(self):
        self.documents.clear()
        self.embeddings.clear()
        self._save_index()


semantic_index = SemanticSearchIndex("search_index.json")


def index_analysis(
    analysis_id: str,
    filename: str,
    content: str,
    metadata: Optional[Dict] = None
):
    semantic_index.add_document(analysis_id, filename, content, metadata)


def search_papers(query: str, top_k: int = 10) -> List[Dict]:
    results = semantic_index.search(query, top_k)
    return [
        {
            "doc_id": doc_id,
            "score": score,
            "snippet": snippet
        }
        for doc_id, score, snippet in results
    ]


def remove_from_index(analysis_id: str):
    semantic_index.remove_document(analysis_id)
