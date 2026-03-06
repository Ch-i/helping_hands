"""Tests for shared conftest fixtures (repo_index, fake_config, make_cli_hand)."""

from __future__ import annotations

from pathlib import Path

from helping_hands.lib.config import Config
from helping_hands.lib.hands.v1.hand.cli.goose import GooseCLIHand
from helping_hands.lib.repo import RepoIndex


class TestRepoIndexFixture:
    def test_returns_repo_index(self, repo_index) -> None:
        assert isinstance(repo_index, RepoIndex)

    def test_contains_stub_files(self, repo_index) -> None:
        assert "main.py" in repo_index.files
        assert "utils.py" in repo_index.files

    def test_backed_by_tmp_path(self, repo_index) -> None:
        assert repo_index.root.exists()


class TestFakeConfigFixture:
    def test_returns_config(self, fake_config) -> None:
        assert isinstance(fake_config, Config)

    def test_model_is_test(self, fake_config) -> None:
        assert fake_config.model == "test-model"

    def test_repo_path_exists(self, fake_config) -> None:
        assert Path(fake_config.repo).exists()


class TestMakeCliHandFixture:
    def test_creates_hand_instance(self, make_cli_hand) -> None:
        hand = make_cli_hand(GooseCLIHand, model="anthropic/test")
        assert isinstance(hand, GooseCLIHand)

    def test_default_model(self, make_cli_hand) -> None:
        hand = make_cli_hand(GooseCLIHand)
        assert hand.config.model == "test-model"

    def test_custom_model(self, make_cli_hand) -> None:
        hand = make_cli_hand(GooseCLIHand, model="openai/gpt-5.2")
        assert hand.config.model == "openai/gpt-5.2"

    def test_has_config_and_repo_index(self, make_cli_hand) -> None:
        hand = make_cli_hand(GooseCLIHand)
        assert hasattr(hand, "config")
        assert isinstance(hand.config, Config)
