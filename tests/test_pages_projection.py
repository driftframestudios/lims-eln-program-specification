from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import pages_projection as pages
from scripts import scan_secret_shapes


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_REVISION = "a" * 40
CANONICAL_ORIGIN = "https://docs.example.org"
CANONICAL_HOST = "docs.example.org"


class PagesProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = pages.SourceProof.fixture(FIXTURE_REVISION)

    def build(
        self,
        base: Path,
        *,
        root: Path = ROOT,
        name: str = "site",
        canonical: bool = False,
    ) -> Path:
        output = base / name
        pages.build_projection(
            output,
            root=root,
            canonical_origin=CANONICAL_ORIGIN if canonical else None,
            cname=CANONICAL_HOST if canonical else None,
            source_proof=self.proof,
        )
        return output

    def load_manifest(self, output: Path) -> dict:
        return json.loads(
            (output / pages.MANIFEST_FILENAME).read_text(encoding="utf-8")
        )

    def write_manifest(self, output: Path, manifest: dict) -> None:
        (output / pages.MANIFEST_FILENAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )

    def reseal_file(self, output: Path, relative_path: str, payload: bytes) -> None:
        path = output / relative_path
        path.write_bytes(payload)
        manifest = self.load_manifest(output)
        record = next(item for item in manifest["files"] if item["path"] == relative_path)
        record["bytes"] = len(payload)
        record["sha256"] = hashlib.sha256(payload).hexdigest()
        self.write_manifest(output, manifest)

    def copy_source_fixture(self, destination: Path) -> Path:
        paths = {
            "AUTHORS",
            "LICENSE",
            "STATUS.yaml",
            "constellation.json",
            "pages/README.md",
            "pages/program-content.json",
            "pyproject.toml",
            "release/repository-role.json",
            "scripts/build_pages.py",
            "scripts/pages_projection.py",
            "scripts/validate_projection.py",
            "scripts/verify_pages.py",
        }
        content = json.loads((ROOT / "pages/program-content.json").read_text())
        paths.update(item["sourcePath"] for item in content["contracts"])
        for relative_path in sorted(paths):
            source = ROOT / relative_path
            target = destination / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        return destination

    def test_fixture_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = self.build(base, name="first")
            second = self.build(base, name="second")
            self.assertEqual(
                pages.snapshot_projection(first), pages.snapshot_projection(second)
            )
            summary = pages.validate_projection(
                first, root=ROOT, allow_fixture=True
            )
            self.assertEqual("valid", summary["status"])
            self.assertEqual(6, summary["htmlPages"])
            self.assertEqual(2, summary["publicSkills"])

    def test_manifest_covers_the_complete_declared_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            manifest = self.load_manifest(output)
            self.assertEqual(pages.MANIFEST_VERSION, manifest["manifestVersion"])
            self.assertEqual(pages.PROJECTION_OWNER, manifest["projectionOwner"])
            self.assertEqual(pages.FILE_SCOPE, manifest["fileScope"])
            self.assertEqual(FIXTURE_REVISION, manifest["sourceRevision"])
            self.assertEqual("fixture", manifest["sourceStanding"])
            self.assertIsNone(manifest["canonicalOrigin"])
            self.assertEqual(
                [
                    "constellation-coherence-reconciliation",
                    "source-authority-mapping",
                ],
                [item["slug"] for item in manifest["publicSkills"]],
            )
            self.assertEqual(
                [
                    ".agents/skills/constellation-coherence-reconciliation/SKILL.md",
                    ".agents/skills/source-authority-mapping/SKILL.md",
                ],
                [item["sourcePath"] for item in manifest["publicSkills"]],
            )
            projected_paths = {item["path"] for item in manifest["files"]}
            self.assertIn("skills/index.html", projected_paths)
            self.assertIn(
                "skills/source-authority-mapping/index.html", projected_paths
            )
            self.assertIn(
                "skills/constellation-coherence-reconciliation/index.html",
                projected_paths,
            )
            expected = {
                path.relative_to(output).as_posix()
                for path in output.rglob("*")
                if path.is_file()
            }
            self.assertEqual(
                expected,
                {item["path"] for item in manifest["files"]}
                | {pages.MANIFEST_FILENAME},
            )

    def test_index_links_the_selected_public_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            index = (output / "index.html").read_text(encoding="utf-8")
            contracts = (output / "contracts" / "index.html").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                'href="https://cometspectrum.io/reports/golden-specimen/comparison.html"',
                index,
            )
            self.assertIn(
                'href="https://kindlight.io/snippets/lims-eln-enterprise-implementation/0.3.2/"',
                index,
            )
            self.assertIn("Idempotency implementation from release 0.3.2", index)
            self.assertIn("complete 94-line implementation", index)
            self.assertIn("Implementation 0.3.2", index)
            self.assertIn(
                "Only the Program coordinate remains a placeholder",
                contracts,
            )
            self.assertIn(
                "Only the Program release coordinate awaits promotion",
                contracts,
            )
            self.assertIn("Program release observation", contracts)
            verification = (
                output / "verification" / "index.html"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "python3 scripts/verify_program_release_observation.py",
                verification,
            )
            self.assertIn(
                "python3 scripts/validate_pinned_sources.py --preflight-external",
                verification,
            )
            self.assertNotIn('target="_blank"', index)

    def test_fixture_standing_requires_explicit_test_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            with self.assertRaisesRegex(pages.ProjectionError, "explicit test"):
                pages.validate_projection(output, root=ROOT)

    def test_clean_source_proof_tracks_exact_head_and_worktree_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            commands = (
                ("git", "init", "--quiet"),
                ("git", "config", "user.name", "Projection Fixture"),
                ("git", "config", "user.email", "fixture@example.invalid"),
                (
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{pages.PROJECTION_OWNER}.git",
                ),
            )
            for command in commands:
                subprocess.run(command, cwd=repository, check=True)
            (repository / "source.txt").write_text("stable\n", encoding="utf-8")
            subprocess.run(("git", "add", "source.txt"), cwd=repository, check=True)
            subprocess.run(
                ("git", "commit", "--quiet", "-m", "Add fixture source"),
                cwd=repository,
                check=True,
            )
            proof = pages.verify_clean_source(repository)
            self.assertEqual("clean", proof.standing)
            self.assertRegex(proof.revision, r"^[0-9a-f]{40}$")

            foreign = Path(temporary) / "foreign"
            foreign.mkdir()
            foreign_commands = (
                ("git", "init", "--quiet"),
                ("git", "config", "user.name", "Foreign Fixture"),
                ("git", "config", "user.email", "foreign@example.invalid"),
                (
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{pages.PROJECTION_OWNER}.git",
                ),
            )
            for command in foreign_commands:
                subprocess.run(command, cwd=foreign, check=True)
            (foreign / "source.txt").write_text("stable\n", encoding="utf-8")
            subprocess.run(("git", "add", "source.txt"), cwd=foreign, check=True)
            subprocess.run(
                ("git", "commit", "--quiet", "-m", "Add foreign source"),
                cwd=foreign,
                check=True,
            )
            foreign_revision = subprocess.run(
                ("git", "rev-parse", "HEAD"),
                cwd=foreign,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertNotEqual(proof.revision, foreign_revision)
            with mock.patch.dict(
                os.environ,
                {
                    "GIT_DIR": str(foreign / ".git"),
                    "GIT_WORK_TREE": str(repository),
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "core.worktree",
                    "GIT_CONFIG_VALUE_0": str(repository),
                },
            ):
                self.assertEqual(proof, pages.verify_clean_source(repository))

            subprocess.run(
                ("git", "remote", "set-url", "origin", "https://github.com/example/other.git"),
                cwd=repository,
                check=True,
            )
            with self.assertRaisesRegex(pages.ProjectionError, "origin differs"):
                pages.verify_clean_source(repository)
            subprocess.run(
                (
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    f"https://github.com/{pages.PROJECTION_OWNER}.git",
                ),
                cwd=repository,
                check=True,
            )

            subprocess.run(
                (
                    "git",
                    "remote",
                    "set-url",
                    "--add",
                    "origin",
                    "https://github.com/example/secondary-wrong.git",
                ),
                cwd=repository,
                check=True,
            )
            with self.assertRaisesRegex(pages.ProjectionError, "origin differs"):
                pages.verify_clean_source(repository)
            subprocess.run(
                ("git", "config", "--unset-all", "remote.origin.url"),
                cwd=repository,
                check=True,
            )
            subprocess.run(
                (
                    "git",
                    "config",
                    "--add",
                    "remote.origin.url",
                    f"https://github.com/{pages.PROJECTION_OWNER}.git",
                ),
                cwd=repository,
                check=True,
            )

            nested = repository / "nested-source"
            nested.mkdir()
            with self.assertRaisesRegex(pages.ProjectionError, "worktree root"):
                pages.verify_clean_source(nested)
            nested.rmdir()

            (repository / "source.txt").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(pages.ProjectionError, "match HEAD"):
                pages.verify_clean_source(repository)

            (repository / "source.txt").write_text("stable\n", encoding="utf-8")
            subprocess.run(
                ("git", "update-index", "--assume-unchanged", "source.txt"),
                cwd=repository,
                check=True,
            )
            (repository / "source.txt").write_text("hidden change\n", encoding="utf-8")
            standing = subprocess.run(
                ("git", "status", "--porcelain=v1", "--untracked-files=all"),
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual("", standing.stdout)
            with self.assertRaisesRegex(pages.ProjectionError, "bytes differ from HEAD"):
                pages.verify_clean_source(repository)

    def test_clean_source_proof_ignores_local_replace_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            for command in (
                ("git", "init", "--quiet"),
                ("git", "config", "user.name", "Projection Fixture"),
                ("git", "config", "user.email", "fixture@example.invalid"),
                (
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{pages.PROJECTION_OWNER}.git",
                ),
            ):
                subprocess.run(command, cwd=repository, check=True)

            source = repository / "source.txt"
            source.write_text("accepted\n", encoding="utf-8")
            subprocess.run(("git", "add", "source.txt"), cwd=repository, check=True)
            subprocess.run(
                ("git", "commit", "--quiet", "-m", "Add accepted source"),
                cwd=repository,
                check=True,
            )
            accepted_revision = subprocess.run(
                ("git", "rev-parse", "HEAD"),
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            source.write_text("replacement\n", encoding="utf-8")
            subprocess.run(("git", "add", "source.txt"), cwd=repository, check=True)
            subprocess.run(
                ("git", "commit", "--quiet", "-m", "Add replacement source"),
                cwd=repository,
                check=True,
            )
            replacement_revision = subprocess.run(
                ("git", "rev-parse", "HEAD"),
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            subprocess.run(
                ("git", "reset", "--soft", accepted_revision),
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ("git", "replace", accepted_revision, replacement_revision),
                cwd=repository,
                check=True,
            )

            masked_status = subprocess.run(
                ("git", "status", "--porcelain=v1", "--untracked-files=all"),
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual("", masked_status.stdout)
            with self.assertRaisesRegex(pages.ProjectionError, "match HEAD"):
                pages.verify_clean_source(repository)

    def test_clean_build_rejects_ignored_untracked_skill_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository = self.copy_source_fixture(base / "repository")
            (repository / ".gitignore").write_text(
                ".agents/skills/\n", encoding="utf-8"
            )
            commands = (
                ("git", "init", "--quiet"),
                ("git", "config", "user.name", "Projection Fixture"),
                ("git", "config", "user.email", "fixture@example.invalid"),
                (
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{pages.PROJECTION_OWNER}.git",
                ),
                ("git", "add", "."),
                ("git", "commit", "--quiet", "-m", "Add fixture source"),
            )
            for command in commands:
                subprocess.run(command, cwd=repository, check=True)

            skill = repository / ".agents" / "skills" / "hidden" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                "---\nname: Hidden\ndescription: Ignored source.\n"
                "source_band: public_ready\n---\n# Hidden\n",
                encoding="utf-8",
            )
            standing = subprocess.run(
                ("git", "status", "--porcelain=v1", "--untracked-files=all"),
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual("", standing.stdout)
            with self.assertRaisesRegex(
                pages.ProjectionError, "regular file in exact HEAD"
            ):
                pages.build_projection(base / "projection", root=repository)

    def test_manifest_authority_fields_are_closed(self) -> None:
        mutations = {
            "manifestVersion": "9.0.0",
            "projectionOwner": "example/other",
            "fileScope": "partial",
            "sourceRevision": "b" * 40,
            "sourceStanding": "unverified",
            "canonicalOrigin": "https://docs.example.org",
        }
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = self.build(base, name="source")
            for field, value in mutations.items():
                with self.subTest(field=field):
                    output = base / f"mutation-{field}"
                    shutil.copytree(source, output)
                    manifest = self.load_manifest(output)
                    manifest[field] = value
                    self.write_manifest(output, manifest)
                    with self.assertRaises(pages.ProjectionError):
                        pages.validate_projection(
                            output, root=ROOT, allow_fixture=True
                        )

    def test_source_proof_fields_move_together(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            manifest = self.load_manifest(output)
            manifest["sourceProof"]["revision"] = "b" * 40
            self.write_manifest(output, manifest)
            with self.assertRaisesRegex(pages.ProjectionError, "sourceProof differ"):
                pages.validate_projection(output, root=ROOT, allow_fixture=True)

    def test_content_digest_binds_source_and_projected_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = self.build(base, name="digest")
            manifest = self.load_manifest(first)
            manifest["programContent"]["sha256"] = "sha256:" + ("b" * 64)
            self.write_manifest(first, manifest)
            with self.assertRaisesRegex(pages.ProjectionError, "content digest"):
                pages.validate_projection(first, root=ROOT, allow_fixture=True)

            second = self.build(base, name="projected-copy")
            content = (second / pages.PROGRAM_CONTENT_OUTPUT).read_bytes() + b"\n"
            self.reseal_file(second, pages.PROGRAM_CONTENT_OUTPUT, content)
            with self.assertRaisesRegex(pages.ProjectionError, "projected program content"):
                pages.validate_projection(second, root=ROOT, allow_fixture=True)

    def test_inventory_addition_and_removal_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            addition = self.build(base, name="addition")
            (addition / "extra.txt").write_text("extra\n", encoding="utf-8")
            with self.assertRaisesRegex(pages.ProjectionError, "inventory differs"):
                pages.validate_projection(addition, root=ROOT, allow_fixture=True)

            removal = self.build(base, name="removal")
            (removal / "assets/styles.css").unlink()
            with self.assertRaisesRegex(pages.ProjectionError, "byte identity differs"):
                pages.validate_projection(removal, root=ROOT, allow_fixture=True)

    def test_canonical_origin_and_cname_form_one_validated_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            output = self.build(base, canonical=True)
            summary = pages.validate_projection(
                output, root=ROOT, allow_fixture=True
            )
            self.assertEqual("valid", summary["status"])
            self.assertEqual(CANONICAL_HOST + "\n", (output / "CNAME").read_text())
            for path in output.rglob("*.html"):
                relative = path.relative_to(output).as_posix()
                parent = Path(relative).parent.as_posix()
                suffix = "/" if parent == "." else f"/{parent}/"
                self.assertIn(
                    f'<link rel="canonical" href="{CANONICAL_ORIGIN}{suffix}">',
                    path.read_text(encoding="utf-8"),
                )
            with self.assertRaises(pages.ProjectionError):
                pages.canonical_pair(CANONICAL_ORIGIN, None)
            with self.assertRaises(pages.ProjectionError):
                pages.canonical_pair(CANONICAL_ORIGIN, "other.example.org")
            with self.assertRaises(pages.ProjectionError):
                pages.canonical_pair("http://docs.example.org", CANONICAL_HOST)

    def test_canonical_html_and_cname_mutations_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            html_output = self.build(base, name="html", canonical=True)
            page_path = "contracts/index.html"
            changed = (html_output / page_path).read_text(encoding="utf-8").replace(
                f'{CANONICAL_ORIGIN}/contracts/',
                "https://other.example.org/contracts/",
            )
            self.reseal_file(html_output, page_path, changed.encode("utf-8"))
            with self.assertRaises(pages.ProjectionError):
                pages.validate_projection(
                    html_output, root=ROOT, allow_fixture=True
                )

            cname_output = self.build(base, name="cname", canonical=True)
            self.reseal_file(cname_output, "CNAME", b"other.example.org\n")
            with self.assertRaisesRegex(pages.ProjectionError, "must match"):
                pages.validate_projection(
                    cname_output, root=ROOT, allow_fixture=True
                )

    def test_full_sha_source_links_and_shared_page_contract_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            source_pattern = re.compile(
                rf"https://github\.com/{re.escape(pages.PROJECTION_OWNER)}/blob/"
                rf"({FIXTURE_REVISION})/[A-Za-z0-9_./~-]+"
            )
            for path in output.rglob("*.html"):
                document = path.read_text(encoding="utf-8")
                visible = html.unescape(document)
                self.assertRegex(document, source_pattern)
                required = (
                    pages.BENCHMARK_DATA_USE_LINE,
                    pages.MAPS_MARKER_LINE,
                    pages.MAPS_GUID_LINE,
                    pages.BIG_BENCH_MARKER_LINE,
                    pages.BIG_BENCH_GUID_LINE,
                    pages.FOOTER_NOTICE,
                )
                positions = [visible.index(item) for item in required]
                self.assertEqual(sorted(positions), positions)
                self.assertIn(
                    f'<meta name="author" content="{pages.ORGANIZATION}">',
                    document,
                )
                self.assertIn(
                    f'<meta name="publisher" content="{pages.ORGANIZATION}">',
                    document,
                )
            self.assertIn(
                ".benchmark-line, .benchmark-marker, .legal { margin: 0; max-width: 62rem; overflow-wrap: anywhere; }",
                (output / "assets/styles.css").read_text(encoding="utf-8"),
            )

    def test_canary_guid_mutation_is_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            page_path = "index.html"
            changed = (output / page_path).read_text(encoding="utf-8").replace(
                pages.MAPS_GUID_LINE,
                "canary GUID changed",
                1,
            )
            with self.assertRaisesRegex(pages.ProjectionError, "benchmark or attribution"):
                pages._validate_html(
                    output,
                    page_path,
                    changed.encode("utf-8"),
                    root=ROOT,
                    proof=self.proof,
                    canonical_origin=None,
                )

    def test_source_link_revision_mutation_is_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            page_path = "index.html"
            changed = (output / page_path).read_text(encoding="utf-8").replace(
                f"/blob/{FIXTURE_REVISION}/", f"/blob/{'b' * 40}/", 1
            )
            self.reseal_file(output, page_path, changed.encode("utf-8"))
            with self.assertRaises(pages.ProjectionError):
                pages.validate_projection(output, root=ROOT, allow_fixture=True)

    def test_public_ready_skill_set_controls_catalog_presence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = self.copy_source_fixture(base / "source")
            skill_sources = {
                "public-guide": (
                    "---\nname: Public guide\ndescription: A public collaboration guide.\n"
                    "source_band: public_ready\n---\n# Public guide\n\nUse this guide.\n"
                ),
                "working-guide": (
                    "---\nname: Working guide\ndescription: A collaboration draft.\n"
                    "source_band: public_possible\n---\n# Working guide\n"
                ),
                "internal-guide": (
                    "---\nname: Internal guide\ndescription: An internal collaboration source.\n"
                    "source_band: internal\n---\n# Internal guide\n"
                ),
            }
            for slug, text in skill_sources.items():
                path = source / ".agents" / "skills" / slug / "SKILL.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            output = self.build(base, root=source, name="projection")
            manifest = self.load_manifest(output)
            self.assertEqual(
                ["public-guide"], [item["slug"] for item in manifest["publicSkills"]]
            )
            self.assertTrue((output / "skills/index.html").is_file())
            self.assertTrue((output / "skills/public-guide/index.html").is_file())
            combined_html = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted(output.rglob("*.html"))
            )
            self.assertIn("Public guide", combined_html)
            self.assertNotIn("Working guide", combined_html)
            self.assertNotIn("Internal guide", combined_html)
            summary = pages.validate_projection(
                output, root=source, allow_fixture=True
            )
            self.assertEqual(1, summary["publicSkills"])

    def test_public_skill_inventory_mutation_is_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.build(Path(temporary))
            manifest = self.load_manifest(output)
            manifest["publicSkills"] = [
                {
                    "name": "Invented",
                    "pagePath": "skills/invented/index.html",
                    "slug": "invented",
                    "sourcePath": ".agents/skills/invented/SKILL.md",
                    "sourceSha256": "sha256:" + ("a" * 64),
                }
            ]
            self.write_manifest(output, manifest)
            with self.assertRaisesRegex(pages.ProjectionError, "skill inventory"):
                pages.validate_projection(output, root=ROOT, allow_fixture=True)

    def test_output_location_and_existing_bytes_are_guarded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            existing = base / "existing"
            existing.mkdir()
            (existing / "keep.txt").write_text("keep\n", encoding="utf-8")
            with self.assertRaisesRegex(pages.ProjectionError, "begin empty"):
                pages.build_projection(
                    existing, source_proof=self.proof
                )
            with self.assertRaisesRegex(pages.ProjectionError, "outside"):
                pages.build_projection(
                    ROOT / ".pages-build" / "fixture",
                    source_proof=self.proof,
                )

            valid = self.build(base, name="valid")
            validation_alias = base / "validation-alias"
            validation_alias.symlink_to(valid, target_is_directory=True)
            with self.assertRaisesRegex(pages.ProjectionError, "symbolic-link"):
                pages.validate_projection(
                    validation_alias,
                    root=ROOT,
                    allow_fixture=True,
                )

            build_parent = base / "build-parent"
            build_parent.mkdir()
            build_parent_alias = base / "build-parent-alias"
            build_parent_alias.symlink_to(build_parent, target_is_directory=True)
            with self.assertRaisesRegex(pages.ProjectionError, "symbolic-link"):
                pages.build_projection(
                    build_parent_alias / "site",
                    source_proof=self.proof,
                )

    def test_generated_output_secret_shape_scan_is_clean_and_live(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            output = self.build(base, name="clean")
            self.assertEqual([], scan_secret_shapes.scan_repository(output))

            canary = "gh" + "p_" + ("Q" * 24)
            canary_root = base / "canary"
            canary_root.mkdir()
            (canary_root / "index.html").write_text(
                f"<p>{canary}</p>\n", encoding="utf-8"
            )
            findings = scan_secret_shapes.scan_repository(canary_root)
            self.assertTrue(findings)
            rendered = "\n".join(str(item) for item in findings)
            self.assertNotIn(canary, rendered)
            self.assertIn("redacted", rendered)


if __name__ == "__main__":
    unittest.main()
