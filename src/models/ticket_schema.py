"""
EngineTriagingSupport - Ticket Analysis Schema
==============================================

Overview
--------
This module defines the `TicketAnalysis` data model, which represents the
structured output returned by the LLM after analyzing a customer support ticket.

The schema enforces strict validation rules for:
- Department classification (controlled vocabulary)
- English summary limits
- Urgency levels
- Detected issues (bugs)

This ensures that downstream services (routing, prioritization, analytics)
receive clean, predictable, and validated data.

Key Features
------------
1. Controlled Department Labels
   - Enforces one of four pre-approved support departments.

2. English Summary Validation
   - Ensures summary length (5–300 chars).
   - Additional rule: no more than two sentences (validated via period count).

3. Urgency Scoring
   - Integer scale: 1 (low) to 5 (critical).

4. Structured Bug Extraction
   - Optional list of detected issues.

5. Full Pydantic Validation
   - Provides strong type guarantees and runtime validation.

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

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class TicketAnalysis(BaseModel):
    """
    Schema representing the standardized output from the ticket analysis engine.

    This model is populated by the LLM classification process and returned
    by the API as the primary structured representation of an analyzed ticket.

    Attributes:
        department (Literal[str]):
            The assigned ticket department. Must match one of the four predefined
            Persian department categories.

        summary_en (str):
            A concise English summary of the issue. Must be 5–300 characters
            and may not exceed two sentences.

        urgency_level (int):
            Urgency score on a scale of 1 (low) to 5 (critical).

        detected_bugs (List[str]):
            Optional list of extracted bug identifiers or issue descriptions.
    """

    department: Literal[
        "فنی و باگ",
        "مالی و فاکتور",
        "فروش و ارتقا",
        "شکایات",
    ]

    summary_en: str = Field(
        ...,
        description="English summary of the issue in maximum two sentences.",
        min_length=5,
        max_length=300,
    )

    urgency_level: int = Field(
        ...,
        ge=1,
        le=5,
        description="Urgency level from 1 (low) to 5 (critical).",
    )

    detected_bugs: List[str] = Field(
        default_factory=list,
        description="List of extracted bug identifiers or issue notes.",
    )

    @field_validator("summary_en")
    @classmethod
    def validate_summary_length(cls, value: str) -> str:
        """
        Ensure the summary does not exceed two sentences.

        Uses a simple heuristic by counting periods. If more than
        four segments appear, the summary is considered too long.

        Args:
            value (str): The provided English summary.

        Returns:
            str: The cleaned and validated summary.

        Raises:
            ValueError: If the summary appears to exceed two sentences.
        """
        text = value.strip()
        if len(text.split(".")) > 4:
            raise ValueError("summary_en appears longer than two sentences.")
        return text
