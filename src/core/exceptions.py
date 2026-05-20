"""
EngineTriagingSupport - Custom Exceptions
=========================================

Overview
--------
This module defines custom exception types used across the ticket
triaging service. They provide a clear and explicit way to distinguish
between different error categories:

- LLM connectivity or API failures
- Invalid or non-conforming LLM output
- Semantic cache read/write issues

Using domain-specific exceptions makes error handling, logging, and
monitoring more structured and easier to reason about.

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


class LLMServiceError(Exception):
    """
    Raised when a call to the LLM provider fails.

    Typical causes include:
        - Network connectivity errors
        - Timeouts
        - Provider-side HTTP errors (e.g., 429, 500)
        - Invalid API key or authentication issues
    """


class OutputValidationError(Exception):
    """
    Raised when the model output cannot be validated against the schema.

    This error indicates that the LLM returned a response that does not
    conform to the expected Pydantic schema (missing fields, wrong types,
    invalid values, malformed JSON, etc.).
    """


class CacheError(Exception):
    """
    Raised when the semantic cache fails.

    Typical causes include:
        - Errors during FAISS index read/write
        - Corrupted or unreadable cache files
        - I/O errors when persisting cache metadata
    """
