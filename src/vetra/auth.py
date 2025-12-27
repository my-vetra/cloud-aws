from __future__ import annotations

from typing import Any, Iterable

from .errors import ForbiddenError, UnauthorizedError


def get_claims(event: dict[str, Any]) -> dict[str, Any]:
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer") or {}
    claims = authorizer.get("claims") or authorizer.get("jwt", {}).get("claims")
    if not claims:
        raise UnauthorizedError("Missing JWT claims from authorizer")
    return claims


def require_groups(claims: dict[str, Any], allowed_groups: Iterable[str]) -> None:
    groups_claim = claims.get("cognito:groups") or claims.get("groups")
    if not groups_claim:
        raise ForbiddenError("User does not belong to any group")
    if isinstance(groups_claim, str):
        groups = set(groups_claim.split(","))
    else:
        groups = set(groups_claim)
    if not groups.intersection(set(allowed_groups)):
        raise ForbiddenError("User is not authorized for this resource")


def principal_from_claims(claims: dict[str, Any]) -> dict[str, str]:
    tenant = claims.get("custom:tenant") or claims.get("tenant") or "default"
    return {
        "sub": claims.get("sub", "unknown"),
        "email": claims.get("email", ""),
        "tenant": tenant,
    }
