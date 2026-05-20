"""
EngineTriagingSupport - Semantic Cache Service
==============================================

Overview
--------
This module provides a semantic caching layer for ticket analysis results.
Instead of reprocessing highly similar support tickets through the LLM, the
service computes vector embeddings and performs approximate similarity matching
using FAISS. If a sufficiently similar ticket has already been analyzed, the
cached result can be returned immediately.

This mechanism reduces:
- LLM cost
- Response latency
- Duplicate computation for repeated or near-duplicate tickets

Key Features
------------
1. Embedding-Based Similarity Search
   - Converts ticket text into dense vector embeddings using a sentence
     transformer model.
   - Uses cosine-style similarity through normalized embeddings and
     FAISS inner-product search.

2. Persistent Vector Index
   - Stores embeddings in a FAISS index on disk.
   - Reloads the index automatically on service startup.

3. Persistent Result Store
   - Saves classification results in a local JSON store.
   - Links FAISS vector IDs to stored structured outputs.

4. Cache Threshold Control
   - Only returns a cached result if similarity exceeds a configurable threshold.

5. Fault-Tolerant Storage
   - Wraps storage failures in a custom `CacheError` exception.
   - Logs all persistence issues for debugging and observability.

Author
------
Elham Esmaeilnia (elham.e.shirvani@gmail.com)

Service
-------
EngineTriagingSupport

Version
-------
1.0.0

Date
----
2026-05-18
"""

import json
import os
from typing import Optional, Dict, Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.core.config import settings
from src.core.exceptions import CacheError
from src.core.logging import get_logger

logger = get_logger(__name__)


class SemanticCache:
    """
    Semantic similarity cache for previously analyzed tickets.

    This class stores vector embeddings of ticket text in a FAISS index and
    associates them with structured analysis results in a persistent JSON store.
    When a new ticket arrives, it can be embedded and compared against existing
    cached entries to determine whether a sufficiently similar result already
    exists.

    Attributes:
        model (SentenceTransformer): Embedding model used to encode text.
        threshold (float): Minimum similarity required for a cache hit.
        index_path (str): File path where the FAISS index is stored.
        store_path (str): File path where the JSON result store is saved.
        dimension (int): Embedding vector dimension.
        index: In-memory FAISS index.
        store (Dict[str, Any]): Mapping of vector IDs to cached results.
    """

    def __init__(self):
        """
        Initialize the semantic cache and load persisted state.

        Loads the embedding model, similarity threshold, FAISS index,
        and JSON result store from disk if available. Otherwise,
        initializes new empty structures.
        """
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.threshold = settings.SIMILARITY_THRESHOLD

        self.index_path = settings.CACHE_INDEX_PATH
        self.store_path = settings.CACHE_STORE_PATH

        self.dimension = self.model.get_embedding_dimension()
        self.index = self._load_or_create_index()
        self.store = self._load_store()

    def _load_or_create_index(self):
        """
        Load the FAISS index from disk or create a new one.

        If the configured index file exists, it is loaded into memory.
        Otherwise, a new flat inner-product index is created.

        Returns:
            faiss.Index: Loaded or newly created FAISS index.
        """
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        return faiss.IndexFlatIP(self.dimension)

    def _load_store(self) -> Dict[str, Any]:
        """
        Load the cache result store from disk.

        Returns:
            Dict[str, Any]: Cached analysis results mapped by vector ID.
        """
        if os.path.exists(self.store_path):
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _persist(self):
        """
        Persist the FAISS index and result store to disk.

        Ensures the target directory exists, then writes both:
        - the FAISS index file
        - the JSON metadata/result store
        """
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)

    def _embed(self, text: str) -> np.ndarray:
        """
        Convert input text into a normalized embedding vector.

        Args:
            text (str): Ticket text to embed.

        Returns:
            np.ndarray: Embedding vector in float32 format.
        """
        emb = self.model.encode([text], normalize_embeddings=True)
        return emb.astype("float32")

    def lookup(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Search the semantic cache for a similar previously processed ticket.

        The input text is embedded and compared against all cached vectors
        using nearest-neighbor search. If the top result exceeds the configured
        similarity threshold, the associated cached analysis result is returned.

        Args:
            text (str): Ticket text to search for.

        Returns:
            Optional[Dict[str, Any]]: Cached structured result if a match is found;
            otherwise `None`.
        """
        if self.index.ntotal == 0:
            return None

        vector = self._embed(text)
        scores, ids = self.index.search(vector, 1)

        similarity = float(scores[0][0])
        idx = int(ids[0][0])

        if similarity >= self.threshold:
            logger.info("Semantic cache hit with similarity %.3f", similarity)
            return self.store.get(str(idx))

        return None

    def store_result(self, text: str, result: Dict[str, Any]):
        """
        Store a new analyzed ticket result in the semantic cache.

        The ticket text is embedded, inserted into the FAISS index,
        associated with the provided structured result, and persisted to disk.

        Args:
            text (str): Ticket text used as the semantic cache key.
            result (Dict[str, Any]): Structured analysis result to store.

        Raises:
            CacheError: If embedding, indexing, or persistence fails.
        """
        try:
            vector = self._embed(text)
            idx = self.index.ntotal

            self.index.add(vector)
            self.store[str(idx)] = result
            self._persist()

        except Exception as exc:
            logger.exception("Failed to store semantic cache")
            raise CacheError(str(exc)) from exc
