"""Tests that documentation indexes stay in sync with actual files.

These tests catch common drift: a new design doc is added but not listed in
the index, or a completed plan is missing from PLANS.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Repo root is two levels up from tests/
REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"


class TestDesignDocsIndex:
    """Every .md file in docs/design-docs/ must be listed in the index."""

    @pytest.fixture()
    def index_text(self) -> str:
        return (DOCS_DIR / "design-docs" / "index.md").read_text()

    @pytest.fixture()
    def design_doc_files(self) -> list[str]:
        dd = DOCS_DIR / "design-docs"
        return sorted(f.name for f in dd.glob("*.md") if f.name != "index.md")

    def test_all_design_docs_listed_in_index(
        self, index_text: str, design_doc_files: list[str]
    ) -> None:
        for filename in design_doc_files:
            assert filename in index_text, (
                f"Design doc '{filename}' exists in docs/design-docs/ "
                f"but is not referenced in design-docs/index.md"
            )

    def test_index_has_no_stale_links(
        self, index_text: str, design_doc_files: list[str]
    ) -> None:
        """Every .md link in the index must point to an actual file."""
        import re

        linked = re.findall(r"\(([^)]+\.md)\)", index_text)
        for link in linked:
            assert link in design_doc_files, (
                f"design-docs/index.md references '{link}' but no such file exists"
            )


class TestPlansTracking:
    """Every file in exec-plans/completed/ must be referenced in PLANS.md."""

    @pytest.fixture()
    def plans_text(self) -> str:
        return (DOCS_DIR / "PLANS.md").read_text()

    @pytest.fixture()
    def completed_plan_files(self) -> list[str]:
        completed = DOCS_DIR / "exec-plans" / "completed"
        if not completed.exists():
            return []
        return sorted(f.name for f in completed.glob("*.md"))

    def test_all_completed_plans_referenced(
        self, plans_text: str, completed_plan_files: list[str]
    ) -> None:
        for filename in completed_plan_files:
            assert filename in plans_text, (
                f"Completed plan '{filename}' exists in exec-plans/completed/ "
                f"but is not referenced in PLANS.md"
            )


class TestDocsIndexCompleteness:
    """docs/index.md should reference all top-level docs/*.md files."""

    @pytest.fixture()
    def index_text(self) -> str:
        return (DOCS_DIR / "index.md").read_text()

    @pytest.fixture()
    def top_level_doc_files(self) -> list[str]:
        return sorted(f.name for f in DOCS_DIR.glob("*.md") if f.name != "index.md")

    def test_all_top_level_docs_referenced(
        self, index_text: str, top_level_doc_files: list[str]
    ) -> None:
        for filename in top_level_doc_files:
            assert filename in index_text, (
                f"Top-level doc '{filename}' exists in docs/ "
                f"but is not referenced in docs/index.md"
            )
