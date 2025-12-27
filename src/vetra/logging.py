from __future__ import annotations

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

from .config import get_settings


settings = get_settings()
logger = Logger(service=settings.service_name, level="INFO")
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace="Vetra", service=settings.service_name)


def with_correlation_id(headers: dict[str, str] | None) -> None:
    correlation_id = None
    if headers:
        correlation_id = headers.get(settings.correlation_header) or headers.get(
            settings.correlation_header.capitalize()
        )
    if correlation_id:
        logger.append_keys(correlation_id=correlation_id)
    metrics.set_default_dimensions(stage=settings.stage)
    metrics.add_metric(name="ColdStart", unit=MetricUnit.Count, value=1)
