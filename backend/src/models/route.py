from typing import Callable, Optional, Union, Literal, Any
from pydantic import BaseModel, Field
from .role import Role


class Route(BaseModel):
    """
    Model representing a FastAPI route configuration
    """
    function: Callable[..., Any] = Field(..., description="Route handler function (sync/async/generator/async generator)")
    description: Optional[str] = Field(None, description="Detailed description of the route")
    path: Optional[str] = Field(None, description="Optional path override for the route")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"] = Field(
        "GET", description="HTTP method for the route"
    )
    summary: Optional[str] = Field(None, description="Short summary of the route")
    tags: Optional[list[str]] = Field(None, description="List of tags for OpenAPI documentation")
    required_roles: Optional[list[Role]] = Field(None, description="Roles allowed to access this endpoint")

    class Config:
        arbitrary_types_allowed = True
