"""
EngineTriagingSupport - Context Optimization Layer
==================================================

Overview
--------
This module defines the `ContextOptimizer`, a lightweight preprocessing layer
responsible for cleaning, normalizing, and compressing raw customer support
ticket text before it is sent to the LLM. Its primary goals are to reduce token
usage, improve response latency, and eliminate noise such as greetings, email
footers, signatures, and thread history.

Key Features
------------
1. Text Normalization
   - Collapses excessive whitespace.
   - Standardizes text structure for downstream components.

2. Noise Removal
   - Removes common greetings (e.g., "Hi", "Hello", “Dear Support”).
   - Strips email signatures, agent signatures, and disclaimers.
   - Removes quoted replies from previous email threads.

3. Length Management
   - Enforces a maximum character limit to cap token usage.
   - Prevents runaway costs when long ticket histories are submitted.

4. Deterministic Processing
   - Entire cleanup pipeline is rule-based, ensuring reproducible results.
   - No external model calls or nondeterministic behavior.

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

from src.core.config import settings
from src.utils.text import (
    normalize_whitespace,
    remove_common_greetings,
    remove_email_signatures,
    remove_quoted_history,
    truncate_text,
)


class ContextOptimizer:
    """
    Preprocess raw ticket text before LLM classification.

    The `ContextOptimizer` applies a series of deterministic transformations to
    reduce noise and irrelevant content from user-provided support tickets.
    This preprocessing step ensures:
    - Lower token consumption for the LLM (cost optimization).
    - Faster response times (latency optimization).
    - Cleaner, more context-focused input for downstream reasoning.

    Attributes:
        enable_llm_compression (bool): Global flag that can toggle heavy
        preprocessing or model-based compression (future extension point).
    """

    def __init__(self):
        """Initialize optimizer flags based on service configuration."""
        self.enable_llm_compression = settings.ENABLE_LLM_COMPRESSION

    def optimize(self, raw_text: str) -> str:
        """
        Clean, normalize, and limit input text length.

        This method performs a deterministic transformation pipeline consisting of:
        1. Whitespace normalization
        2. Removal of common greetings
        3. Removal of email signatures and disclaimers
        4. Removal of quoted conversation history
        5. Hard truncation to a safe maximum length

        Args:
            raw_text (str): The raw customer support ticket text.

        Returns:
            str: The cleaned and compressed text ready for LLM ingestion.
        """
        text = normalize_whitespace(raw_text)
        text = remove_common_greetings(text)
        text = remove_email_signatures(text)
        text = remove_quoted_history(text)

        # Hard truncation safety guard
        text = truncate_text(text, max_chars=1500)

        return text.strip()
