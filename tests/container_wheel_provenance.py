"""Distinguish installed wheel ownership from source/editable import routing."""
import json
from pathlib import Path


def require_wheel_provenance(distribution, package_file: Path, checkout: Path) -> None:
    wheel = distribution.read_text("WHEEL")
    direct = json.loads(distribution.read_text("direct_url.json") or "{}")
    if not isinstance(wheel, str) or not wheel.startswith("Wheel-Version:"):
        raise ValueError("wheel-metadata-required")
    if not isinstance(direct, dict):
        raise ValueError("direct-url-object-required")
    directory = direct.get("dir_info", {})
    if not isinstance(directory, dict) or directory.get("editable") is True:
        raise ValueError("installed-wheel-required")
    actual = package_file.resolve(strict=True)
    expected = Path(distribution.locate_file("lims_eln_contracts/__init__.py")).resolve(strict=True)
    if actual != expected or actual.is_relative_to(checkout.resolve(strict=True)):
        raise ValueError("installed-package-owner-required")
