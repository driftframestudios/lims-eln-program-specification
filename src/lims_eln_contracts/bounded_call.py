"""Service-owned operation contracts for bounded human and machine callers."""

from __future__ import annotations

from enum import StrEnum
import re
from typing import Literal, Mapping

from pydantic import (
    Field,
    JsonValue,
    NonNegativeInt,
    PositiveInt,
    model_validator,
)

from .canonical import canonical_sha256
from .primitives import (
    ContractModel,
    FieldName,
    Identifier,
    NonEmptyText,
    OperationName,
    SemanticVersion,
    Sha256Digest,
    UpperIdentifier,
    UtcTimestamp,
)


class CallerClass(StrEnum):
    HUMAN_OPERATOR = "human_operator"
    SERVICE_WORKLOAD = "service_workload"
    WORKFLOW_AUTOMATION = "workflow_automation"
    AI_BOUNDED_CALLER = "ai_bounded_caller"


class EffectClass(StrEnum):
    READ = "read"
    NARROW_IDEMPOTENT_WRITE = "narrow_idempotent_write"
    APPROVAL_GATED_BROAD_WRITE = "approval_gated_broad_write"


class CallDecision(StrEnum):
    AUTHORIZED = "authorized"
    SUCCEEDED = "succeeded"
    REPLAYED = "replayed"
    DENIED = "denied"
    RECOVERY_REQUIRED = "recovery_required"


class EffectState(StrEnum):
    ZERO_EFFECT = "zero_effect"
    CONFIRMED_EFFECT = "confirmed_effect"
    RECOVERY_OWNED = "recovery_owned"


class InputValueKind(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    OBJECT = "object"
    ARRAY = "array"
    BOOLEAN = "boolean"
    SHA256_DIGEST = "sha256_digest"


class OperationSemanticError(ValueError):
    """A call can proceed after its request aligns with the released operation."""


class OperationInputField(ContractModel):
    name: FieldName
    value_kind: InputValueKind
    required: bool = True
    purpose: NonEmptyText
    minimum: int | None = None
    minimum_length: NonNegativeInt | None = None
    pattern: NonEmptyText | None = None

    @model_validator(mode="after")
    def constraints_match_value_kind(self) -> "OperationInputField":
        if self.minimum is not None and self.value_kind is not InputValueKind.INTEGER:
            raise ValueError("minimum accompanies an integer input field")
        if self.minimum_length is not None and self.value_kind not in {
            InputValueKind.STRING,
            InputValueKind.SHA256_DIGEST,
            InputValueKind.OBJECT,
            InputValueKind.ARRAY,
        }:
            raise ValueError(
                "minimum_length accompanies a string, digest, object, or array input field"
            )
        if self.pattern is not None:
            if self.value_kind not in {
                InputValueKind.STRING,
                InputValueKind.SHA256_DIGEST,
            }:
                raise ValueError("pattern accompanies a string-shaped input field")
            try:
                re.compile(self.pattern)
            except re.error as error:
                raise ValueError("pattern carries a valid regular expression") from error
        return self

    def validate_value(self, value: JsonValue) -> None:
        kind_matches = {
            InputValueKind.STRING: lambda item: type(item) is str,
            InputValueKind.INTEGER: lambda item: type(item) is int,
            InputValueKind.OBJECT: lambda item: type(item) is dict,
            InputValueKind.ARRAY: lambda item: type(item) is list,
            InputValueKind.BOOLEAN: lambda item: type(item) is bool,
            InputValueKind.SHA256_DIGEST: lambda item: (
                type(item) is str
                and re.fullmatch(r"sha256:[a-f0-9]{64}", item) is not None
            ),
        }
        if not kind_matches[self.value_kind](value):
            raise OperationSemanticError(
                f"payload field {self.name!r} uses {self.value_kind.value}; "
                "supply the released value shape"
            )
        if self.minimum is not None and isinstance(value, int) and value < self.minimum:
            raise OperationSemanticError(
                f"payload field {self.name!r} starts at {self.minimum}"
            )
        if self.minimum_length is not None and isinstance(value, (str, list, dict)):
            if len(value) < self.minimum_length:
                raise OperationSemanticError(
                    f"payload field {self.name!r} carries at least "
                    f"{self.minimum_length} item(s)"
                )
        if self.pattern is not None and isinstance(value, str):
            if re.fullmatch(self.pattern, value) is None:
                raise OperationSemanticError(
                    f"payload field {self.name!r} follows its released pattern"
                )


class OperationInputContract(ContractModel):
    declared_fields_only: Literal[True] = True
    fields: tuple[OperationInputField, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def field_names_remain_unique(self) -> "OperationInputContract":
        names = [field.name for field in self.fields]
        if len(names) != len(set(names)):
            raise ValueError("operation input field names remain unique")
        return self

    @property
    def required_fields(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields if field.required)

    def validate_payload(self, payload: Mapping[str, JsonValue]) -> None:
        released = {field.name: field for field in self.fields}
        supplied = set(payload)
        missing = set(self.required_fields) - supplied
        if missing:
            raise OperationSemanticError(
                "payload supplies every required field; add " + ", ".join(sorted(missing))
            )
        outside_contract = supplied - set(released)
        if outside_contract:
            raise OperationSemanticError(
                "payload stays within the released field set; route these fields "
                "through contract review: "
                + ", ".join(sorted(outside_contract))
            )
        for name, value in payload.items():
            released[name].validate_value(value)


class OperationBudgets(ContractModel):
    record_limit: PositiveInt
    depth_limit: PositiveInt
    attempt_limit: PositiveInt
    timeout_seconds: PositiveInt


class EffectCeiling(ContractModel):
    record_limit: PositiveInt
    editable_fields: tuple[FieldName, ...] = ()
    resource_types: tuple[FieldName, ...] = Field(min_length=1)
    preflight_match_required: bool

    @model_validator(mode="after")
    def ceiling_members_remain_unique(self) -> "EffectCeiling":
        if len(self.editable_fields) != len(set(self.editable_fields)):
            raise ValueError("editable_fields remain unique")
        if len(self.resource_types) != len(set(self.resource_types)):
            raise ValueError("resource_types remain unique")
        return self


class OperationContract(ContractModel):
    operation_id: UpperIdentifier
    version: SemanticVersion
    name: OperationName
    effect_class: EffectClass
    allowed_callers: tuple[CallerClass, ...] = Field(min_length=1)
    input_contract: OperationInputContract
    output_contract: NonEmptyText
    budgets: OperationBudgets
    effect_ceiling: EffectCeiling
    approval_binding: tuple[FieldName, ...] = ()
    recovery_state: NonEmptyText

    @model_validator(mode="after")
    def operation_semantics_remain_bounded(self) -> "OperationContract":
        if len(self.allowed_callers) != len(set(self.allowed_callers)):
            raise ValueError("allowed_callers remain unique")
        if len(self.approval_binding) != len(set(self.approval_binding)):
            raise ValueError("approval_binding fields remain unique")
        if self.effect_ceiling.record_limit > self.budgets.record_limit:
            raise ValueError("effect ceiling stays within the operation record budget")
        if self.effect_class is EffectClass.READ and self.effect_ceiling.editable_fields:
            raise ValueError("read operations preserve stored fields with an empty editable set")
        if self.effect_class is EffectClass.NARROW_IDEMPOTENT_WRITE:
            if self.effect_ceiling.record_limit != 1:
                raise ValueError("narrow idempotent writes carry a one-record effect ceiling")
            if not self.effect_ceiling.editable_fields:
                raise ValueError("narrow idempotent writes name their editable field set")
            if "idempotency_key" not in self.input_contract.required_fields:
                raise ValueError("narrow idempotent writes require idempotency_key")
        if self.effect_class is EffectClass.APPROVAL_GATED_BROAD_WRITE:
            accountable_callers = {
                CallerClass.HUMAN_OPERATOR,
                CallerClass.WORKFLOW_AUTOMATION,
            }
            if not set(self.allowed_callers).issubset(accountable_callers):
                raise ValueError(
                    "broad-write callers remain human operators or released workflows; "
                    "route other requests through accountable approval"
                )
            if not self.approval_binding:
                raise ValueError("broad writes bind an attributable approval field set")
            if self.budgets.attempt_limit != 1:
                raise ValueError("broad writes carry one execution attempt per approval")
        elif self.approval_binding:
            raise ValueError(
                "caller policy governs read and narrow-write operations; "
                "approval_binding remains reserved for broad writes"
            )
        return self

    def validate_payload(self, payload: Mapping[str, JsonValue]) -> None:
        self.input_contract.validate_payload(payload)
        patch = payload.get("patch")
        if patch is not None and self.effect_ceiling.editable_fields:
            if not isinstance(patch, dict) or not patch:
                raise OperationSemanticError("patch supplies at least one editable field")
            requested_fields = set(patch)
            editable_fields = set(self.effect_ceiling.editable_fields)
            protected = requested_fields - editable_fields
            if protected:
                raise OperationSemanticError(
                    "patch stays within the released editable field set; route these "
                    "fields to accountable review: "
                    + ", ".join(sorted(protected))
                )
        planned_effect_count = payload.get("planned_effect_count")
        if isinstance(planned_effect_count, int):
            if planned_effect_count > self.effect_ceiling.record_limit:
                raise OperationSemanticError(
                    "planned effect count stays within the released ceiling of "
                    f"{self.effect_ceiling.record_limit}"
                )


class BoundedCallRequest(ContractModel):
    request_version: SemanticVersion = "1.0.0"
    call_id: Identifier
    caller_class: CallerClass
    caller_identity: Identifier
    initiating_principal: Identifier
    operation_id: UpperIdentifier
    operation_version: SemanticVersion
    tenant_id: Identifier
    purpose: NonEmptyText
    payload: dict[str, JsonValue]
    requested_at: UtcTimestamp
    correlation_id: Identifier
    approval_receipt_id: Identifier | None = None

    def canonical_digest(self) -> str:
        return canonical_sha256(self)


class OperationCatalog(ContractModel):
    catalog_version: SemanticVersion
    contract_id: UpperIdentifier
    operations: tuple[OperationContract, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def operation_identities_remain_unique(self) -> "OperationCatalog":
        identities = [operation.operation_id for operation in self.operations]
        names = [operation.name for operation in self.operations]
        if len(identities) != len(set(identities)):
            raise ValueError("operation identifiers remain unique")
        if len(names) != len(set(names)):
            raise ValueError("operation names remain unique")
        return self

    def operation(self, operation_id: str) -> OperationContract:
        for operation in self.operations:
            if operation.operation_id == operation_id:
                return operation
        raise OperationSemanticError(
            f"operation_id {operation_id!r} uses the released catalog; "
            "select one of " + ", ".join(item.operation_id for item in self.operations)
        )

    def bind(self, request: BoundedCallRequest) -> OperationContract:
        operation = self.operation(request.operation_id)
        if request.operation_version != operation.version:
            raise OperationSemanticError(
                f"operation version stays at {operation.version}; refresh the request contract"
            )
        if request.caller_class not in operation.allowed_callers:
            raise OperationSemanticError(
                f"{operation.operation_id} serves "
                + ", ".join(caller.value for caller in operation.allowed_callers)
                + "; route this caller through an eligible operation"
            )
        operation.validate_payload(request.payload)
        payload_tenant = request.payload.get("tenant_id")
        if payload_tenant != request.tenant_id:
            raise OperationSemanticError(
                "authenticated tenant and payload tenant remain identical; "
                "rebuild the request from authenticated context"
            )
        if (
            operation.effect_class is EffectClass.APPROVAL_GATED_BROAD_WRITE
            and request.approval_receipt_id is None
        ):
            raise OperationSemanticError(
                "broad writes carry an approval_receipt_id; "
                "route the request through accountable approval"
            )
        if operation.effect_class is EffectClass.APPROVAL_GATED_BROAD_WRITE:
            payload_approval = request.payload.get("approval_receipt_id")
            if payload_approval != request.approval_receipt_id:
                raise OperationSemanticError(
                    "request and payload carry one approval_receipt_id; "
                    "rebuild the request from the approved receipt"
                )
        return operation


class EffectSummary(ContractModel):
    state: EffectState
    record_count: NonNegativeInt | None
    resource_ids: tuple[Identifier, ...] = ()
    changed_fields: tuple[FieldName, ...] = ()

    @model_validator(mode="after")
    def effect_state_remains_explicit(self) -> "EffectSummary":
        if len(self.resource_ids) != len(set(self.resource_ids)):
            raise ValueError("effect resource identifiers remain unique")
        if len(self.changed_fields) != len(set(self.changed_fields)):
            raise ValueError("changed fields remain unique")
        if self.state is EffectState.ZERO_EFFECT and self.record_count != 0:
            raise ValueError("zero_effect carries record_count 0")
        if self.state is EffectState.CONFIRMED_EFFECT:
            if self.record_count is None or self.record_count < 1:
                raise ValueError("confirmed_effect carries a positive record_count")
        if self.state is EffectState.RECOVERY_OWNED and self.record_count is not None:
            raise ValueError(
                "recovery_owned preserves an unsettled record_count; "
                "record the confirmed count after reconciliation"
            )
        return self


class BoundedCallReceipt(ContractModel):
    receipt_version: SemanticVersion = "1.0.0"
    receipt_id: Identifier
    occurred_at: UtcTimestamp
    caller_class: CallerClass
    caller_identity: Identifier
    initiating_principal: Identifier
    operation_id: UpperIdentifier
    operation_version: SemanticVersion
    tenant_id: Identifier
    request_digest: Sha256Digest
    decision: CallDecision
    effect_summary: EffectSummary
    evidence_locator: NonEmptyText
    correlation_id: Identifier
    reason_code: FieldName
    next_action: NonEmptyText

    @model_validator(mode="after")
    def decision_carries_its_replacement_state(self) -> "BoundedCallReceipt":
        if self.decision is CallDecision.DENIED:
            if self.effect_summary.state is not EffectState.ZERO_EFFECT:
                raise ValueError(
                    "denied calls carry zero_effect and a next action inside the released boundary"
                )
        if self.decision is CallDecision.RECOVERY_REQUIRED:
            if self.effect_summary.state is not EffectState.RECOVERY_OWNED:
                raise ValueError(
                    "recovery_required carries recovery_owned effect state and an "
                    "accountable next action"
                )
        if re.fullmatch(r"[a-z][a-z0-9+.-]*://[^?#]+", self.evidence_locator) is None:
            raise ValueError("evidence_locator uses an absolute governed URI")
        return self
