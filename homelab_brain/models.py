"""Pydantic models for type safety"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class Response(BaseModel):
    """Response from the Brain"""
    answer: str = Field(description="Natural language answer")
    confidence: float = Field(ge=0.0, le=1.0, description="AI confidence score")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Supporting metrics")
    duration_ms: float = Field(description="Query duration in milliseconds")
    context_gathered: list[str] = Field(default_factory=list, description="What context was used")
    timestamp: datetime = Field(default_factory=datetime.now)


class Metric(BaseModel):
    """A single metric observation"""
    entity: str = Field(description="What this metric is about (e.g., 'lab01', 'gitlab-runner')")
    attribute: str = Field(description="What is being measured (e.g., 'cpu_percent', 'memory_mb')")
    value: Any = Field(description="The measured value")
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemContext(BaseModel):
    """Context gathered from the system"""
    cpu: Optional[dict[str, Any]] = None
    memory: Optional[dict[str, Any]] = None
    disk: Optional[dict[str, Any]] = None
    docker: Optional[dict[str, Any]] = None
    health: Optional[dict[str, Any]] = None
    network: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
