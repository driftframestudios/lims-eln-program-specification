"""Strict JSON parsing and one stable canonical SHA-256 representation."""

from __future__ import annotations

from enum import Enum
import hashlib
import json
import math
from typing import Any, TypeVar

from pydantic import BaseModel


class ContractJsonError(ValueError):
    """Base error for a JSON value outside the shared contract boundary."""


class DuplicateObjectKeyError(ContractJsonError):
    """A JSON object needs one value for each unique key."""


class NonFiniteNumberError(ContractJsonError):
    """Contract numbers occupy the finite JSON number domain."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateObjectKeyError(
                f"JSON object key {key!r} appears more than once; "
                "supply one attributable value for that key"
            )
        result[key] = value
    return result


def _finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise NonFiniteNumberError(
            f"numeric token {token!r} exceeds the finite JSON domain; "
            "supply a finite measurement or an explicit textual state"
        )
    return value


def _json_constant(token: str) -> None:
    raise NonFiniteNumberError(
        f"numeric token {token!r} is outside JSON; "
        "supply a finite measurement or an explicit textual state"
    )


def strict_json_loads(payload: str | bytes | bytearray) -> Any:
    """Parse JSON with unique object keys and finite numeric values."""

    return json.loads(
        payload,
        object_pairs_hook=_unique_object,
        parse_constant=_json_constant,
        parse_float=_finite_float,
    )


def _json_ready(value: Any, path: str = "$") -> Any:
    if isinstance(value, BaseModel):
        return _json_ready(value.model_dump(mode="json", by_alias=True), path)
    if isinstance(value, Enum):
        return _json_ready(value.value, path)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise NonFiniteNumberError(
                f"{path} carries a non-finite number; "
                "supply a finite measurement or an explicit textual state"
            )
        return value
    if isinstance(value, (list, tuple)):
        return [_json_ready(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, dict):
        document: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractJsonError(
                    f"{path} uses key {key!r}; JSON object keys remain strings"
                )
            document[key] = _json_ready(item, f"{path}.{key}")
        return document
    raise ContractJsonError(
        f"{path} carries {type(value).__name__}; "
        "supply a JSON scalar, array, object, or contract model"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a contract value into stable UTF-8 JSON bytes."""

    document = _json_ready(value)
    return json.dumps(
        document,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    """Return the prefixed SHA-256 digest of canonical JSON bytes."""

    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


ModelT = TypeVar("ModelT", bound=BaseModel)


def model_from_strict_json(model_type: type[ModelT], payload: str | bytes) -> ModelT:
    """Validate a model after the JSON boundary proves uniqueness and finiteness."""

    strict_json_loads(payload)
    return model_type.model_validate_json(payload, strict=True)

