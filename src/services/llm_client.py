"""
SupportTriagingEngine - LLM Client Service
==========================================

Overview
--------
This module provides a lightweight client responsible for communicating
with OpenAI-compatible Large Language Model (LLM) APIs.

It sends chat-completion requests to the configured model provider and
returns generated responses used for ticket triaging and classification.

The client is intentionally minimal and provider-agnostic, meaning it
can communicate with any service that implements the OpenAI Chat
Completions API specification (e.g., OpenRouter, OpenAI, local gateways).

Key Features
------------
1. OpenAI-Compatible API
   Uses the standard `/chat/completions` endpoint.

2. Deterministic Classification
   The temperature parameter is fixed to `0` to ensure consistent
   classification outputs.

3. Centralized Configuration
   All runtime parameters (API key, model, timeout) are loaded from
   the service configuration.

4. Structured Error Handling
   Network failures, API errors, and malformed responses are captured
   and converted into a unified `LLMServiceError`.

5. Observability
   Failures are logged using the central logging system to support
   debugging and monitoring.

Author
------
Elham Esmaeilnia (elham.e.shirvani@gmail.com)

Service
-------
SupportTriagingEngine

Version
-------
1.1.0

Date
----
2026-05-18
"""

import requests
from typing import Dict, Any

from src.core.config import settings
from src.core.exceptions import LLMServiceError
from src.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    Lightweight client for interacting with OpenAI-compatible LLM APIs.

    This class abstracts HTTP communication with a language model provider
    and exposes a simple `chat()` method used by the ticket orchestration
    pipeline.

    Attributes
    ----------
    base_url : str
        Base URL of the LLM provider API.

    api_key : str
        Authentication token used for API access.

    model : str
        Name of the LLM model used for inference.

    timeout : int
        Maximum duration (in seconds) to wait for an API response.
    """

    def __init__(self):
        """
        Initialize the LLM client using values from the service configuration.
        """
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a chat-completion request to the configured LLM provider.

        The request follows the OpenAI Chat Completions format and contains
        two messages:

        - A **system prompt** that defines the model's role and behavior.
        - A **user prompt** containing the ticket text to analyze.

        Parameters
        ----------
        system_prompt : str
            Instructional prompt guiding the LLM behavior.

        user_prompt : str
            Input ticket text that needs to be analyzed.

        Returns
        -------
        str
            The textual response produced by the language model.

        Raises
        ------
        LLMServiceError
            Raised if the API request fails due to network errors,
            provider errors, rate limits, or malformed responses.
        """

        url = f"{self.base_url}/chat/completions"

        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            # Raises HTTPError for 4xx / 5xx responses
            response.raise_for_status()

            data: Dict[str, Any] = response.json()

            try:
                content = data["choices"][0]["message"]["content"]

                if content is None or not isinstance(content, str) or not content.strip():
                    raise LLMServiceError("LLM returned empty content")

                return content

            except (KeyError, IndexError, TypeError) as exc:
                logger.error("Unexpected LLM response format: %s", data)
                raise LLMServiceError(
                    "Unexpected response format from LLM provider"
                ) from exc

        except requests.exceptions.Timeout as exc:
            logger.error("LLM request timed out")
            raise LLMServiceError("LLM request timed out") from exc

        except requests.exceptions.HTTPError as exc:
            logger.error(
                "LLM provider returned HTTP error: %s - %s",
                response.status_code,
                response.text,
            )
            raise LLMServiceError(
                f"LLM provider error: {response.status_code}"
            ) from exc

        except requests.exceptions.RequestException as exc:
            logger.error("Network error while calling LLM")
            raise LLMServiceError("Network error while contacting LLM") from exc

        except ValueError as exc:
            logger.error("Invalid JSON response from LLM provider")
            raise LLMServiceError("Invalid JSON response from LLM") from exc
