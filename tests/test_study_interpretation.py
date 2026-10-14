"""Literal counterexamples for declared equality and profile eligibility."""
from copy import deepcopy
import json
import unittest

from pydantic import ValidationError
from lims_eln_contracts import admit_administrative_study, canonical_sha256
from lims_eln_contracts.resources import load_administrative_study_example
from lims_eln_contracts.study_interpretation import StudyAnalysisProfile, StudyInterpretation, interpret_administrative_study


def admit(document):
    runs = {r["run_id"]: r for r in document["runs"]}
    for observation in document["observations"]:
        observation["specification_digest"] = canonical_sha256(document["specification"])
        observation["input_digest"] = canonical_sha256(runs[observation["run_id"]])
    return admit_administrative_study(json.dumps(document).encode())


class InterpretationTests(unittest.TestCase):
    def test_import_binds_comparable_oracle_availability(self):
        source = load_administrative_study_example().model_dump(mode="json")
        for present in (True, False):
            with self.subTest(present=present):
                document = deepcopy(source)
                if not present:
                    document["expected_pairs"] = []
                profile = StudyAnalysisProfile(require_expected_pair=True)
                forged = interpret_administrative_study(admit(document), profile).model_dump(mode="json")
                for pair in forged["pairs"]:
                    pair.update(expected_pair_available=not present, eligible=not present, reasons=["expected_pair_unavailable"] if present else [])
                forged.update(expected_pairs_available=0 if present else 2, eligible_pairs=0 if present else 2, excluded_pairs=2 if present else 0)
                with self.assertRaisesRegex(ValidationError, "oracle availability"):
                    StudyInterpretation.model_validate_json(json.dumps(forged))

    def test_import_requires_execution_for_completed_arms(self):
        source = load_administrative_study_example().model_dump(mode="json")
        source["observations"][0]["execution"]["model_id"] = "different-model"
        forged = interpret_administrative_study(admit(source)).model_dump(mode="json")
        pair = next(item for item in forged["pairs"] if item["execution"] == "mismatched")
        pair.update(execution="unavailable", reasons=["execution_unavailable"])
        with self.assertRaisesRegex(ValidationError, "completed arms"):
            StudyInterpretation.model_validate_json(json.dumps(forged))

    def setUp(self):
        self.document = load_administrative_study_example().model_dump(mode="json")
        self.profile = StudyAnalysisProfile(profile_id="specified-age-control", required_specified_controls=("age_band",))

    def test_all_presence_standings_keep_declared_equality_separate(self):
        for standing in ("specified", "unknown", "omitted", "unmeasured", "withheld"):
            with self.subTest(standing=standing):
                document = deepcopy(self.document)
                for run in document["runs"]:
                    control = next(f for f in run["factors"] if f["name"] == "age_band")
                    control.update(standing=standing, value="adult" if standing == "specified" else None)
                study = admit(document)
                basic = interpret_administrative_study(study)
                strict = interpret_administrative_study(study, self.profile)
                self.assertEqual((basic.planned_pairs, basic.eligible_pairs, basic.usable_runs), (2, 2, 4))
                self.assertEqual(strict.eligible_pairs, 2 if standing == "specified" else 0)
                self.assertEqual(strict.pairs[0].reasons, () if standing == "specified" else ("required_control_unspecified:age_band",))
                self.assertEqual(strict.pairs[0].controls[0].a.standing, standing)
                self.assertEqual(strict.comparison.comparisons[0].standing, "comparable")

    def test_asymmetric_presence_and_unequal_values(self):
        for standing, value, reasons in (
            ("specified", "child", ("controlled_input_mismatch",)),
            ("withheld", None, ("controlled_input_mismatch", "required_control_unspecified:age_band")),
        ):
            with self.subTest(standing=standing):
                document = deepcopy(self.document)
                document["runs"][1]["factors"][1].update(standing=standing, value=value)
                observed = interpret_administrative_study(admit(document), self.profile)
                self.assertEqual(observed.pairs[0].reasons, reasons)
                self.assertEqual((observed.eligible_pairs, observed.excluded_pairs), (1, 1))

    def test_missing_outputs_execution_and_expected_pair_are_independent(self):
        cases = ("missing_arm", "failed", "execution", "missing_oracle")
        for case in cases:
            with self.subTest(case=case):
                document = deepcopy(self.document)
                if case == "missing_arm":
                    document["observations"].pop(1)
                    reasons = ("execution_unavailable", "output_unavailable")
                elif case == "failed":
                    document["observations"][1].update(status="failed", reason_code="fixture_failure", scientific_output=None, administrative_output=None)
                    reasons = ("output_unavailable",)
                elif case == "execution":
                    document["observations"][1]["execution"]["model_id"] = "alternate-model"
                    reasons = ("execution_mismatched",)
                else:
                    document["expected_pairs"].pop(0)
                    reasons = ("expected_pair_unavailable",)
                profile = StudyAnalysisProfile(require_expected_pair=True)
                observed = interpret_administrative_study(admit(document), profile)
                self.assertEqual(observed.pairs[0].reasons, reasons)
                self.assertEqual(observed.planned_pairs, 2)
                self.assertEqual(observed.usable_runs, 3 if case in {"missing_arm", "failed"} else 4)

    def test_order_and_roundtrip_preserve_interpretation(self):
        first = interpret_administrative_study(admit(deepcopy(self.document)), self.profile)
        self.document["runs"].reverse()
        self.document["observations"].reverse()
        for run in self.document["runs"]:
            run["factors"].reverse()
        reordered = interpret_administrative_study(admit(self.document), self.profile)
        self.assertEqual(first.pairs, reordered.pairs)
        self.assertNotEqual(first.study_digest, reordered.study_digest)
        self.assertEqual(first, StudyInterpretation.model_validate_json(first.model_dump_json(), strict=True))

    def test_imported_summary_and_reasons_require_consistency(self):
        original = interpret_administrative_study(admit(self.document)).model_dump(mode="json")
        for defect in ("counts", "reason", "eligibility", "duplicate", "binding"):
            with self.subTest(defect=defect):
                document = deepcopy(original)
                if defect == "counts": document["eligible_pairs"] = 0
                elif defect == "reason": document["pairs"][0]["reasons"] = ["invented_reason"]
                elif defect == "eligibility": document["pairs"][0]["eligible"] = False
                elif defect == "duplicate": document["pairs"][1] = document["pairs"][0]
                else: document["study_digest"] = canonical_sha256("different study")
                with self.assertRaises(ValidationError):
                    StudyInterpretation.model_validate_json(json.dumps(document), strict=True)

    def test_profile_controls_are_unique_and_declared(self):
        with self.assertRaises(ValidationError):
            StudyAnalysisProfile(required_specified_controls=("age_band", "age_band"))
        with self.assertRaisesRegex(ValueError, "declared controlled factors"):
            interpret_administrative_study(admit(self.document), StudyAnalysisProfile(required_specified_controls=("missing_factor",)))
