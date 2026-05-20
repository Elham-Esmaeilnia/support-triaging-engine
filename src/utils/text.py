"""
SupportTriagingEngine - Text Preprocessing Utilities
====================================================

Overview
--------
This module provides a collection of lightweight, deterministic text-cleaning
utilities used in the ticket preprocessing pipeline. These functions are designed
to remove noise, normalize formatting, and safely truncate support ticket text
before it is passed to the LLM.

All transformations are rule-based and rely on regular expressions to ensure:
- Predictable behavior
- Zero external dependencies
- High performance
- Language-aware cleanup (English + Persian)

Key Functionalities
-------------------
1. Whitespace Normalization
   - Standardizes newline characters.
   - Collapses excessive spaces and blank lines.

2. Greeting Removal
   - Removes common English and Persian greetings at the beginning of tickets.

3. Signature Removal
   - Strips common email sign-offs and mobile footers.

4. Quoted History Removal
   - Detects and removes previous email thread history.

5. Safe Truncation
   - Limits character length while preserving whole words.

Author
------
Elham Esmaeilnia (elham.e.shirvani@gmail.com)

Service
-------
SupportTriagingEngine

Version
-------
1.0.0

Date
----
2026-05-18
"""

import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace and line breaks in text.

    - Converts Windows-style CRLF to LF.
    - Collapses multiple spaces/tabs into a single space.
    - Reduces excessive blank lines to a maximum of two.

    Args:
        text (str): Input text.

    Returns:
        str: Cleaned text with standardized whitespace.
    """
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_common_greetings(text: str) -> str:
    """
    Remove common greeting phrases at the beginning of a ticket.

    Supports English and Persian greetings.

    Args:
        text (str): Input ticket text.

    Returns:
        str: Text without leading greeting phrases.
    """
    greeting_patterns = [
        r"^\s*(hi|hello|dear support|dear team|سلام|درود)[\s,!.]*",
        r"^\s*(good morning|good afternoon|good evening)[\s,!.]*",
    ]
    for pattern in greeting_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    return text.strip()


def remove_email_signatures(text: str) -> str:
    """
    Remove common email signatures and sign-off phrases.

    Detects both English and Persian closing patterns,
    including mobile email footers.

    Args:
        text (str): Input ticket text.

    Returns:
        str: Text without trailing signature sections.
    """
    signature_patterns = [
        r"(?is)\n(best regards|kind regards|regards|thanks|thank you|با احترام|ارادتمند).*?$",
        r"(?is)\n(sent from my iphone).*?$",
    ]
    for pattern in signature_patterns:
        text = re.sub(pattern, "", text)
    return text.strip()


def remove_quoted_history(text: str) -> str:
    """
    Remove quoted email thread history from the ticket.

    Attempts to detect markers such as:
    - "On <date> wrote:"
    - "From: "

    If a quoted history marker is found, returns only the
    newest portion of the conversation.

    Args:
        text (str): Input ticket text.

    Returns:
        str: Ticket content without previous thread history.
    """
    patterns = [
        r"(?is)^.*?(?=\nOn .* wrote:)",
        r"(?is)^.*?(?=\nFrom: )",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return text.strip()


def truncate_text(text: str, max_chars: int) -> str:
    """
    Safely truncate text to a maximum character limit.

    Ensures truncation does not cut words in half by trimming
    back to the last full word boundary.

    Args:
        text (str): Input ticket text.
        max_chars (int): Maximum allowed character length.

    Returns:
        str: Truncated text within the specified limit.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].strip()
