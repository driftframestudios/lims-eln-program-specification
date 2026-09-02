"""Stable primitives shared by the LIMS/ELN contract models."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, StringConstraints


_UTC_TIMESTAMP = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?Z$"
)


def _utc_timestamp_remains_valid(value: str) -> str:
    """Return one canonical UTC timestamp after proving its calendar value."""

    if _UTC_TIMESTAMP.fullmatch(value) is None:
        raise ValueError("timestamp uses an RFC 3339 UTC value ending in Z")
    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as error:
        raise ValueError("timestamp names a valid UTC calendar instant") from error
    return value


class ContractModel(BaseModel):
    """Base boundary whose values stay strict, immutable, and fully declared."""

    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        frozen=True,
        serialize_by_alias=True,
        strict=True,
        validate_by_alias=True,
        validate_by_name=True,
        validate_default=True,
    )


Identifier = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{1,126}[A-Za-z0-9]$",
    ),
]
UpperIdentifier = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=128,
        pattern=r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$",
    ),
]
FieldName = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=96,
        pattern=r"^[a-z][a-z0-9_]*$",
    ),
]
OperationName = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=96,
        pattern=r"^[a-z][a-z0-9_]*$",
    ),
]
SemanticVersion = Annotated[
    str,
    StringConstraints(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"),
]
Sha256Digest = Annotated[
    str,
    StringConstraints(pattern=r"^sha256:[a-f0-9]{64}$"),
]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
UtcTimestamp = Annotated[
    str,
    StringConstraints(min_length=20, max_length=27),
    AfterValidator(_utc_timestamp_remains_valid),
]

