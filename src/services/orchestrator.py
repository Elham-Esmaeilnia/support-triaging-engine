"""
EngineTriagingSupport - Ticket Orchestration Pipeline
=====================================================

Overview
--------
This module defines the `TicketOrchestrator` class — the central controller that
coordinates the multi-stage workflow of analyzing customer support tickets using
LLM-based reasoning, semantic similarity caching, and structured schema validation.

It integrates multiple subsystems:

- **ContextOptimizer:** Refines the raw text to produce concise and relevant input
  for the LLM, improving prompt quality and reducing noise.
- **SemanticCache:** Stores previously processed tickets using semantic similarity
  to reduce redundant LLM calls and improve system efficiency.
- **LLMClient:** Communicates with an external Large Language Model provider
  (e.g., OpenRouter or Hugging Face) to perform classification and analysis.
- **TicketAnalysis (Pydantic model):** Ensures that all LLM outputs conform to a
  strict schema before being returned to downstream services.

Processing Flow
---------------
1. **Context Optimization**
   The raw ticket text is cleaned and normalized using `ContextOptimizer`.

2. **Semantic Cache Lookup**
   The system checks whether a semantically similar ticket has already been
   processed. If found, the cached structured response is returned immediately.

3. **LLM Invocation**
   If no cached result exists, the optimized ticket text is sent to the LLM
   using a predefined system prompt that instructs the model how to structure
   its output.

4. **Validation**
   The LLM response is parsed as JSON and validated against the `TicketAnalysis`
   Pydantic schema to guarantee structural correctness.

5. **Caching**
   Successfully validated results are stored in the semantic cache to avoid
   future redundant LLM calls.

Error Handling
--------------
The orchestrator implements robust exception management to maintain system
availability and reliability.

- **LLM Connection Failures**
  If the LLM provider cannot be reached or returns a transport-level error,
  the system logs the failure and retries the request according to the
  configured retry limit.

- **Invalid or Malformed LLM Output**
  If the model returns malformed JSON or data that does not satisfy the
  Pydantic schema, the system logs the issue and retries the request.

- **Cache Failures**
  Cache read/write errors are logged but do not interrupt processing.
  The system continues operating without cache access.

- **Graceful Fallback**
  If all retry attempts fail, the system returns a safe fallback
  `TicketAnalysis` object to ensure the API remains operational and the
  service receives a valid structured response.

Author
------
Elham Esmaeilnia (elham.e.shirvani@gmail.com)

Service
-------
EngineTriagingSupport

Version
-------
1.1.0

Date
----
2026-05-18
"""

import json

from pydantic import ValidationError

from src.core.exceptions import OutputValidationError, LLMServiceError
from src.core.logging import get_logger
from src.models.ticket_schema import TicketAnalysis
from src.services.context_optimizer import ContextOptimizer
from src.services.llm_client import LLMClient
from src.services.semantic_cache import SemanticCache

logger = get_logger(__name__)


class TicketOrchestrator:
    """
    Central orchestration component for the ticket triaging pipeline.

    The `TicketOrchestrator` coordinates the entire analysis workflow
    from raw customer input to validated structured output.

    Responsibilities
    ----------------
    - Preprocess incoming ticket text using the context optimizer.
    - Retrieve previously computed results from the semantic cache.
    - Communicate with the external LLM provider for ticket analysis.
    - Validate model responses using the strict `TicketAnalysis` schema.
    - Store validated results in the semantic cache.
    - Handle failures gracefully without crashing the service.

    Attributes
    ----------
    optimizer : ContextOptimizer
        Component responsible for cleaning and optimizing ticket text.

    llm : LLMClient
        Client used to communicate with the external language model.

    cache : SemanticCache
        Local semantic similarity cache used to store previous results.

    system_prompt : str
        Static prompt template that instructs the LLM how to analyze
        and structure ticket classification responses.
    """

    def __init__(self):
        """
        Initialize the orchestration pipeline.

        This method creates instances of all pipeline components and
        loads the system prompt used for LLM interaction.
        """
        self.optimizer = ContextOptimizer()
        self.llm = LLMClient()
        self.cache = SemanticCache()

        with open("src/prompts/ticket_analysis.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def process(self, raw_text: str) -> TicketAnalysis:
        """
        Execute the full ticket triaging workflow.

        The method performs preprocessing, semantic cache lookup,
        LLM invocation, output validation, and caching of results.

        Exception management ensures the service remains operational
        even if certain subsystems fail.

        Parameters
        ----------
        raw_text : str
            The original support ticket text submitted by the user.

        Returns
        -------
        TicketAnalysis
            A validated structured representation of the ticket,
            including department routing, English summary,
            urgency level, and detected bug indicators.

        Notes
        -----
        The system applies retry logic for both LLM connection failures
        and invalid model outputs. If all retry attempts fail, a safe
        fallback response is returned to ensure the system remains
        responsive and the service receives a valid structured result.
        """

        from src.core.config import settings

        optimized_text = self.optimizer.optimize(raw_text)

        # --------------------------------------------------
        # 1. Semantic Cache Lookup (Fail-Safe)
        # --------------------------------------------------

        try:
            cached = self.cache.lookup(optimized_text)
            if cached:
                logger.info("Cache hit for incoming ticket.")
                return TicketAnalysis(**cached)

        except Exception as exc:
            logger.error("Cache lookup failed: %s", str(exc))

        last_error = None

        # --------------------------------------------------
        # 2. LLM Invocation with Retry Logic
        # --------------------------------------------------

        for attempt in range(settings.MAX_LLM_RETRIES + 1):

            logger.info("Calling LLM (attempt %d)", attempt + 1)

            try:
                response = self.llm.chat(
                    system_prompt=self.system_prompt,
                    user_prompt=optimized_text,
                )

                parsed = json.loads(response)
                ticket = TicketAnalysis(**parsed)

                # --------------------------------------------------
                # 3. Store Result in Cache (Fail-Safe)
                # --------------------------------------------------

                try:
                    self.cache.store_result(
                        optimized_text,
                        ticket.model_dump(),
                    )
                except Exception as cache_exc:
                    logger.error("Cache store failed: %s", str(cache_exc))

                return ticket

            except LLMServiceError as exc:
                logger.error(
                    "LLM connection failure on attempt %d: %s",
                    attempt + 1,
                    str(exc),
                )
                last_error = exc

            except (json.JSONDecodeError, ValidationError) as exc:
                logger.warning(
                    "Invalid LLM output on attempt %d: %s",
                    attempt + 1,
                    str(exc),
                )
                last_error = exc

        # --------------------------------------------------
        # 4. Graceful Fallback Response
        # --------------------------------------------------

        logger.critical(
            "All LLM attempts failed. Returning fallback response. Last error: %s",
            str(last_error),
        )

        return TicketAnalysis(
            department="شکایات",
            summary_en="Ticket could not be automatically processed due to temporary system issues.",
            urgency_level=3,
            detected_bugs=[],
        )
