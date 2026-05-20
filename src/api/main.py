"""
EngineTriagingSupport API
=========================

Overview
--------
This module exposes the REST API for the EngineTriagingSupport service, a microservice
designed to automatically analyze and triage customer support tickets using an LLM-powered
processing pipeline.

The API receives raw ticket text from support systems, forwards it to the internal
TicketOrchestrator pipeline, and returns structured analysis including department routing,
urgency level, summarized issue description, and potential bug detection.

Key Features
------------
1. Ticket Analysis Endpoint
   - Accepts raw support ticket text.
   - Sends input through the orchestration pipeline.
   - Returns validated structured output using a Pydantic schema.

2. Robust Error Handling
   - Captures unexpected service failures.
   - Returns standardized HTTP responses.
   - Logs internal errors for observability.

3. Modular Architecture
   - Delegates all business logic to `TicketOrchestrator`.
   - Keeps the API layer lightweight and focused on transport.

4. Production-Oriented Setup
   - Centralized logging initialization.
   - Pydantic request validation.
   - Clean JSON responses ready for downstream services.

Inputs
------
POST /triage

Request Body:
{
    "text": "Customer support ticket content"
}

Outputs
-------
JSON response representing structured ticket analysis, for example:

{
    "department": "فنی و باگ",
    "summary_en": "Customer reports payment gateway failure",
    "urgency": 3,
    "bugs": ["payment timeout"]
}

Author
------
Elham Esmaeilnia (elham.e.shirvani@gmail.com)

Service
-------
EngineTriagingSupport
-------

Date
----
2026-05-18
----

Version
-------
1.0.0
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.core.logging import setup_logging, get_logger
from src.services.orchestrator import TicketOrchestrator


# Initialize logging
setup_logging()
logger = get_logger(__name__)


# Initialize API application
app = FastAPI(
    title="EngineTriagingSupport",
    description="LLM-powered microservice for automated support ticket triaging",
    version="1.0.0",
)


# Initialize orchestrator
orchestrator = TicketOrchestrator()


class TicketRequest(BaseModel):
    """
    Request schema for ticket triage.
    """

    text: str = Field(
        ...,
        min_length=5,
        description="Raw support ticket text submitted by the customer."
    )


@app.post("/triage")
async def triage_ticket(request: TicketRequest):
    """
    Analyze and triage a support ticket.

    This endpoint processes raw ticket text through the ticket orchestration
    pipeline and returns a structured classification result.
    """

    try:
        result = orchestrator.process(request.text)
        return result.model_dump()

    except Exception as exc:
        logger.exception("Ticket triage failed")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during ticket processing."
        )

