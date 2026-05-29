from typing import AsyncGenerator, Optional, Any
from pydantic import BaseModel
from fastapi import Request
from sse_starlette.sse import EventSourceResponse
import json


class SSEEvent(BaseModel):
    """
    Standard SSE Event format
    """
    status: str
    message: str
    data: Optional[Any] = None


class SSEOutput:
    """
    Standard SSE response wrapper
    """

    @staticmethod
    def stream(
        request: Request,
        generator: AsyncGenerator[Any, None],
    ) -> EventSourceResponse:
        """
        Wrap an async generator in standardized SSE format
        """

        async def event_wrapper():
            try:
                async for item in generator:

                    if await request.is_disconnected():
                        break

                    event = SSEEvent(
                        status="success",
                        message="streaming",
                        data=item,
                    )

                    yield {
                        "event": "message",
                        "data": json.dumps(event.model_dump()),
                    }

                # Send final completion event
                yield {
                    "event": "end",
                    "data": json.dumps(
                        SSEEvent(
                            status="success",
                            message="completed",
                        ).model_dump()
                    ),
                }

            except Exception as e:
                error_event = SSEEvent(
                    status="error",
                    message=str(e),
                )

                yield {
                    "event": "error",
                    "data": json.dumps(error_event.model_dump()),
                }

        return EventSourceResponse(event_wrapper())