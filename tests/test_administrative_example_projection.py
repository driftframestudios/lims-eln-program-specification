from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_administrative_examples import (  # noqa: E402
    RESOURCE_ROOT,
    rendered_administrative_examples,
)


class AdministrativeExampleProjectionTests(unittest.TestCase):
    def test_examples_are_exact_canonical_bundle_projections(self) -> None:
        for relative_path, expected in rendered_administrative_examples().items():
            with self.subTest(relative_path=relative_path):
                self.assertEqual(expected, (RESOURCE_ROOT / relative_path).read_bytes())


if __name__ == "__main__":
    unittest.main()
