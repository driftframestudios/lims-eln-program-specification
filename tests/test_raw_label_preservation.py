from __future__ import annotations

from copy import deepcopy
import json
import unittest

from pydantic import ValidationError

from lims_eln_contracts.administrative_admission import (
    AdministrativeAdmissionError,
    AdministrativeAdmissionLimits,
    admit_administrative_contract,
)
from lims_eln_contracts.canonical import model_from_strict_json
from lims_eln_contracts.external_administrative import (
    ClassificationState,
    IdentifiedTerm,
    InsuranceClassification,
)
from lims_eln_contracts.resources import load_external_administrative_contract_set


SOURCE_LABELS = (
    " Commercial ",
    "\tCommercial\n",
    "Commercial  plan",
    "\u00a0Commercial\u2003",
    "\n\t\u212b coverage\r\n",
)
REVIEW_LIMITS = AdministrativeAdmissionLimits(
    max_input_bytes=2 * 1024 * 1024,
    max_json_depth=32,
    max_decoded_values=200_000,
    max_records=2_000,
    max_provenance_edges=8_000,
    max_graph_steps=100_000,
    max_output_bytes=2 * 1024 * 1024,
)


class RawLabelPreservationTests(unittest.TestCase):
    def classification_document(self) -> dict:
        bundle = load_external_administrative_contract_set()
        item = next(
            item for item in bundle.insurance_classifications
            if item.state is ClassificationState.CLASSIFIED
        )
        return item.model_dump(mode="json")

    def test_source_strings_survive_model_round_trips_without_input_mutation(self) -> None:
        for raw in SOURCE_LABELS:
            with self.subTest(raw=repr(raw)):
                document = self.classification_document()
                document["raw_label"] = raw
                previous = deepcopy(document)
                parsed = model_from_strict_json(
                    InsuranceClassification, json.dumps(document)
                )
                self.assertEqual(raw, parsed.raw_label)
                serialized = parsed.model_dump_json()
                self.assertEqual(raw, json.loads(serialized)["raw_label"])
                restored = model_from_strict_json(InsuranceClassification, serialized)
                self.assertEqual(raw, restored.raw_label)
                self.assertEqual(parsed, restored)
                self.assertEqual(previous, document)

    def test_empty_blank_and_nontext_values_retain_rejection(self) -> None:
        for raw in ("", " \t\r\n", "\u00a0\u2003", 0, False, [], {}):
            with self.subTest(raw=repr(raw)):
                document = self.classification_document()
                document["raw_label"] = raw
                with self.assertRaises(ValidationError) as caught:
                    model_from_strict_json(
                        InsuranceClassification, json.dumps(document)
                    )
                self.assertIn(
                    ("raw_label",),
                    [item["loc"] for item in caught.exception.errors()],
                )

    def test_null_and_required_field_keep_their_state_contract(self) -> None:
        classified = self.classification_document()
        classified["raw_label"] = None
        with self.assertRaisesRegex(ValidationError, "only unknown"):
            model_from_strict_json(InsuranceClassification, json.dumps(classified))

        unknown = deepcopy(classified)
        unknown.update(
            state="unknown",
            assigned_terms=[],
            candidate_terms=[],
            multiple=False,
            ambiguity="Source label is unavailable in this input.",
        )
        parsed = model_from_strict_json(InsuranceClassification, json.dumps(unknown))
        self.assertIsNone(parsed.raw_label)
        self.assertEqual(ClassificationState.UNKNOWN, parsed.state)
        del unknown["raw_label"]
        with self.assertRaises(ValidationError) as caught:
            model_from_strict_json(InsuranceClassification, json.dumps(unknown))
        self.assertIn(
            ("raw_label",), [item["loc"] for item in caught.exception.errors()]
        )

    def test_normalized_vocabulary_label_retains_its_separate_behavior(self) -> None:
        term = IdentifiedTerm(
            term_id="TERM-ROUNDTRIP",
            label=" Normalized label ",
            vocabulary_id="VOCAB-ROUNDTRIP",
            vocabulary_version="1.0",
        )
        self.assertEqual("Normalized label", term.label)

    def test_bounded_admission_preserves_source_and_accepted_output(self) -> None:
        for raw in SOURCE_LABELS:
            with self.subTest(raw=repr(raw)):
                document = load_external_administrative_contract_set().model_dump(
                    mode="json"
                )
                document["insurance_classifications"][0]["raw_label"] = raw
                payload = json.dumps(document, ensure_ascii=False).encode("utf-8")
                accepted = admit_administrative_contract(payload, limits=REVIEW_LIMITS)
                previous = accepted.canonical_bytes
                restored = json.loads(previous)
                self.assertEqual(
                    raw, restored["insurance_classifications"][0]["raw_label"]
                )
                self.assertEqual(raw, accepted.contract.insurance_classifications[0].raw_label)
                repeated = admit_administrative_contract(previous, limits=REVIEW_LIMITS)
                self.assertEqual(previous, repeated.canonical_bytes)

                rejected = deepcopy(document)
                rejected["insurance_classifications"][0]["raw_label"] = " \t\n"
                with self.assertRaises(AdministrativeAdmissionError) as caught:
                    admit_administrative_contract(
                        json.dumps(rejected).encode("utf-8"), limits=REVIEW_LIMITS
                    )
                self.assertEqual("contract_validation", caught.exception.code)
                self.assertEqual(previous, accepted.canonical_bytes)


if __name__ == "__main__":
    unittest.main()
