"""Shared pytest fixtures for the helping_hands test suite."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from helping_hands.lib.config import Config
from helping_hands.lib.repo import RepoIndex


@pytest.fixture()
def repo_index(tmp_path: Path) -> RepoIndex:
    """A minimal RepoIndex backed by tmp_path with two stub files."""
    (tmp_path / "main.py").write_text("")
    (tmp_path / "utils.py").write_text("")
    return RepoIndex.from_path(tmp_path)


@pytest.fixture()
def fake_config(tmp_path: Path) -> Config:
    """A Config pointing at tmp_path with a test model."""
    return Config(repo=str(tmp_path), model="test-model")


@pytest.fixture()
def make_cli_hand(tmp_path: Path) -> Callable[..., Any]:
    """Factory fixture for CLI hand instances backed by tmp_path.

    Usage::

        def test_something(make_cli_hand):
            hand = make_cli_hand(ClaudeCodeHand, model="claude-sonnet-4-5")
    """

    def _factory(hand_cls: type, model: str = "test-model") -> Any:
        (tmp_path / "main.py").write_text("")
        config = Config(repo=str(tmp_path), model=model)
        ri = RepoIndex.from_path(tmp_path)
        return hand_cls(config=config, repo_index=ri)

    return _factory
