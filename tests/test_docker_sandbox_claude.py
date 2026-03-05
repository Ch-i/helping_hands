"""Tests for DockerSandboxClaudeCodeHand pure/static helper methods."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from helping_hands.lib.config import Config
from helping_hands.lib.hands.v1.hand.cli.docker_sandbox_claude import (
    DockerSandboxClaudeCodeHand,
)
from helping_hands.lib.repo import RepoIndex

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_hand(tmp_path, model="claude-sonnet-4-5"):
    (tmp_path / "main.py").write_text("")
    config = Config(repo=str(tmp_path), model=model)
    repo_index = RepoIndex.from_path(tmp_path)
    return DockerSandboxClaudeCodeHand(config=config, repo_index=repo_index)


@pytest.fixture()
def hand(tmp_path):
    return _make_hand(tmp_path)


# ---------------------------------------------------------------------------
# Class attributes
# ---------------------------------------------------------------------------


class TestClassAttributes:
    def test_backend_name(self) -> None:
        assert DockerSandboxClaudeCodeHand._BACKEND_NAME == "docker-sandbox-claude"

    def test_cli_label(self) -> None:
        assert DockerSandboxClaudeCodeHand._CLI_LABEL == "docker-sandbox"

    def test_cli_display_name(self) -> None:
        assert (
            DockerSandboxClaudeCodeHand._CLI_DISPLAY_NAME
            == "Docker Sandbox Claude Code"
        )

    def test_container_env_vars_disabled(self) -> None:
        assert DockerSandboxClaudeCodeHand._CONTAINER_ENABLED_ENV_VAR == ""
        assert DockerSandboxClaudeCodeHand._CONTAINER_IMAGE_ENV_VAR == ""


# ---------------------------------------------------------------------------
# _resolve_sandbox_name
# ---------------------------------------------------------------------------


class TestResolveSandboxName:
    def test_env_var_override(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "my-sandbox")
        name = hand._resolve_sandbox_name()
        assert name == "my-sandbox"

    def test_env_var_override_stripped(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "  my-sandbox  ")
        name = hand._resolve_sandbox_name()
        assert name == "my-sandbox"

    def test_auto_generated_from_repo_name(self, hand, monkeypatch) -> None:
        monkeypatch.delenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", raising=False)
        name = hand._resolve_sandbox_name()
        assert name.startswith("hh-")
        # Should contain sanitized repo dir name and a hex suffix
        parts = name.split("-")
        assert len(parts[-1]) == 8  # uuid hex suffix

    def test_special_characters_sanitized(self, tmp_path, monkeypatch) -> None:
        # Create a directory with special chars
        repo_dir = tmp_path / "my_repo@v2.0!"
        repo_dir.mkdir()
        (repo_dir / "main.py").write_text("")
        config = Config(repo=str(repo_dir), model="claude-sonnet-4-5")
        repo_index = RepoIndex.from_path(repo_dir)
        hand = DockerSandboxClaudeCodeHand(config=config, repo_index=repo_index)
        monkeypatch.delenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", raising=False)

        name = hand._resolve_sandbox_name()
        # No special chars except hyphens
        assert name.startswith("hh-")
        # The core part should only have alphanumeric and hyphens
        for char in name[3:]:
            assert char.isalnum() or char == "-"

    def test_cached_on_second_call(self, hand, monkeypatch) -> None:
        monkeypatch.delenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", raising=False)
        first = hand._resolve_sandbox_name()
        second = hand._resolve_sandbox_name()
        assert first == second

    def test_preexisting_name_returned(self, hand) -> None:
        hand._sandbox_name = "already-set"
        assert hand._resolve_sandbox_name() == "already-set"


# ---------------------------------------------------------------------------
# _should_cleanup
# ---------------------------------------------------------------------------


class TestShouldCleanup:
    def test_default_is_true(self, hand, monkeypatch) -> None:
        monkeypatch.delenv("HELPING_HANDS_DOCKER_SANDBOX_CLEANUP", raising=False)
        assert hand._should_cleanup() is True

    def test_set_to_zero_returns_false(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_CLEANUP", "0")
        assert hand._should_cleanup() is False

    def test_set_to_one_returns_true(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_CLEANUP", "1")
        assert hand._should_cleanup() is True

    def test_set_to_false_returns_false(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_CLEANUP", "false")
        assert hand._should_cleanup() is False

    def test_set_to_true_returns_true(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_CLEANUP", "true")
        assert hand._should_cleanup() is True


# ---------------------------------------------------------------------------
# _execution_mode
# ---------------------------------------------------------------------------


class TestExecutionMode:
    def test_returns_docker_sandbox(self, hand) -> None:
        assert hand._execution_mode() == "docker-sandbox"


# ---------------------------------------------------------------------------
# _wrap_sandbox_exec
# ---------------------------------------------------------------------------


class TestWrapSandboxExec:
    def test_basic_wrapping(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "test-sb")
        # Clear env vars that might be forwarded
        for key in hand._effective_container_env_names():
            monkeypatch.delenv(key, raising=False)

        result = hand._wrap_sandbox_exec(["claude", "-p", "hello"])
        assert result[0] == "docker"
        assert result[1] == "sandbox"
        assert result[2] == "exec"
        assert "--workdir" in result
        assert "test-sb" in result
        assert result[-3:] == ["claude", "-p", "hello"]

    def test_env_var_forwarding(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "test-sb")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test123")

        result = hand._wrap_sandbox_exec(["claude", "-p", "hello"])
        # Should contain --env flag with the API key
        env_idx = None
        for i, arg in enumerate(result):
            if (
                arg == "--env"
                and i + 1 < len(result)
                and result[i + 1].startswith("ANTHROPIC_API_KEY=")
            ):
                env_idx = i
                break
        assert env_idx is not None, "ANTHROPIC_API_KEY should be forwarded"
        assert result[env_idx + 1] == "ANTHROPIC_API_KEY=sk-ant-test123"


# ---------------------------------------------------------------------------
# _build_failure_message
# ---------------------------------------------------------------------------


class TestBuildFailureMessage:
    def test_auth_not_logged_in(self, hand) -> None:
        msg = hand._build_failure_message(
            return_code=1, output="Error: not logged in to Claude"
        )
        assert "not authenticated" in msg.lower() or "ANTHROPIC_API_KEY" in msg
        assert "Docker sandbox" in msg or "docker-sandbox-claude" in msg.lower()

    def test_auth_authentication_failed(self, hand) -> None:
        msg = hand._build_failure_message(return_code=1, output="authentication_failed")
        assert "ANTHROPIC_API_KEY" in msg
        assert "sandbox" in msg.lower()

    def test_generic_failure_appends_sandbox_note(self, hand, monkeypatch) -> None:
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "my-sb")
        msg = hand._build_failure_message(return_code=42, output="something went wrong")
        assert "my-sb" in msg
        assert "sandbox" in msg.lower()

    def test_no_duplicate_sandbox_note(self, hand, monkeypatch) -> None:
        """If base message already mentions 'sandbox', don't append again."""
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "my-sb")
        # The auth path already mentions sandbox
        msg = hand._build_failure_message(return_code=1, output="not logged in")
        # Count occurrences of "sandbox" — auth message says "Docker sandbox"
        assert "sandbox" in msg.lower()


# ---------------------------------------------------------------------------
# _command_not_found_message
# ---------------------------------------------------------------------------


class TestCommandNotFoundMessage:
    def test_includes_command_name(self, hand) -> None:
        msg = hand._command_not_found_message("claude")
        assert "claude" in msg
        assert "Docker sandbox" in msg
        assert "sandbox template" in msg.lower()


# ---------------------------------------------------------------------------
# _fallback_command_when_not_found
# ---------------------------------------------------------------------------


class TestFallbackCommandWhenNotFound:
    def test_returns_none(self, hand) -> None:
        assert hand._fallback_command_when_not_found(["claude", "-p"]) is None


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_initial_state(self, hand) -> None:
        assert hand._sandbox_name is None
        assert hand._sandbox_created is False


# ---------------------------------------------------------------------------
# _docker_sandbox_available (async, mocked subprocess)
# ---------------------------------------------------------------------------


class TestDockerSandboxAvailable:
    def test_returns_true_on_success(self) -> None:
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = asyncio.new_event_loop().run_until_complete(
                DockerSandboxClaudeCodeHand._docker_sandbox_available()
            )
        assert result is True

    def test_returns_false_on_failure(self) -> None:
        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = asyncio.new_event_loop().run_until_complete(
                DockerSandboxClaudeCodeHand._docker_sandbox_available()
            )
        assert result is False

    def test_returns_false_on_file_not_found(self) -> None:
        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=FileNotFoundError("docker not found"),
        ):
            result = asyncio.new_event_loop().run_until_complete(
                DockerSandboxClaudeCodeHand._docker_sandbox_available()
            )
        assert result is False


# ---------------------------------------------------------------------------
# _ensure_sandbox (async, mocked subprocess)
# ---------------------------------------------------------------------------


class TestEnsureSandbox:
    def test_skips_if_already_created(self, hand) -> None:
        hand._sandbox_created = True
        emit = AsyncMock()
        asyncio.new_event_loop().run_until_complete(hand._ensure_sandbox(emit))
        emit.assert_not_awaited()

    def test_raises_if_docker_not_found(self, hand, monkeypatch) -> None:
        monkeypatch.setattr(
            "helping_hands.lib.hands.v1.hand.cli.docker_sandbox_claude.shutil.which",
            lambda cmd: None,
        )
        emit = AsyncMock()
        with pytest.raises(RuntimeError, match="Docker CLI not found"):
            asyncio.new_event_loop().run_until_complete(hand._ensure_sandbox(emit))

    def test_raises_if_sandbox_plugin_unavailable(self, hand, monkeypatch) -> None:
        monkeypatch.setattr(
            "helping_hands.lib.hands.v1.hand.cli.docker_sandbox_claude.shutil.which",
            lambda cmd: "/usr/bin/docker",
        )
        with patch.object(
            DockerSandboxClaudeCodeHand,
            "_docker_sandbox_available",
            new_callable=AsyncMock,
            return_value=False,
        ):
            emit = AsyncMock()
            with pytest.raises(RuntimeError, match=r"docker sandbox.*not available"):
                asyncio.new_event_loop().run_until_complete(hand._ensure_sandbox(emit))

    def test_creates_sandbox_successfully(self, hand, monkeypatch) -> None:
        monkeypatch.setattr(
            "helping_hands.lib.hands.v1.hand.cli.docker_sandbox_claude.shutil.which",
            lambda cmd: "/usr/bin/docker",
        )
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "test-sb")
        monkeypatch.delenv("HELPING_HANDS_DOCKER_SANDBOX_TEMPLATE", raising=False)

        # Mock _docker_sandbox_available
        with patch.object(
            DockerSandboxClaudeCodeHand,
            "_docker_sandbox_available",
            new_callable=AsyncMock,
            return_value=True,
        ):
            # Mock subprocess for sandbox creation
            mock_stdout = AsyncMock()
            mock_stdout.read = AsyncMock(side_effect=[b"sandbox ready\n", b""])
            mock_proc = AsyncMock()
            mock_proc.stdout = mock_stdout
            mock_proc.returncode = 0
            mock_proc.wait = AsyncMock()

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                emit = AsyncMock()
                asyncio.new_event_loop().run_until_complete(hand._ensure_sandbox(emit))

        assert hand._sandbox_created is True

    def test_raises_on_create_failure(self, hand, monkeypatch) -> None:
        monkeypatch.setattr(
            "helping_hands.lib.hands.v1.hand.cli.docker_sandbox_claude.shutil.which",
            lambda cmd: "/usr/bin/docker",
        )
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "test-sb")
        monkeypatch.delenv("HELPING_HANDS_DOCKER_SANDBOX_TEMPLATE", raising=False)

        with patch.object(
            DockerSandboxClaudeCodeHand,
            "_docker_sandbox_available",
            new_callable=AsyncMock,
            return_value=True,
        ):
            mock_stdout = AsyncMock()
            mock_stdout.read = AsyncMock(side_effect=[b"error: quota exceeded\n", b""])
            mock_proc = AsyncMock()
            mock_proc.stdout = mock_stdout
            mock_proc.returncode = 1
            mock_proc.wait = AsyncMock()

            with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
                emit = AsyncMock()
                with pytest.raises(RuntimeError, match="Failed to create"):
                    asyncio.new_event_loop().run_until_complete(
                        hand._ensure_sandbox(emit)
                    )

    def test_template_env_var_applied(self, hand, monkeypatch) -> None:
        monkeypatch.setattr(
            "helping_hands.lib.hands.v1.hand.cli.docker_sandbox_claude.shutil.which",
            lambda cmd: "/usr/bin/docker",
        )
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "test-sb")
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_TEMPLATE", "my-template")

        with patch.object(
            DockerSandboxClaudeCodeHand,
            "_docker_sandbox_available",
            new_callable=AsyncMock,
            return_value=True,
        ):
            mock_stdout = AsyncMock()
            mock_stdout.read = AsyncMock(side_effect=[b"ok\n", b""])
            mock_proc = AsyncMock()
            mock_proc.stdout = mock_stdout
            mock_proc.returncode = 0
            mock_proc.wait = AsyncMock()

            calls = []

            async def capture_create(*args, **kwargs):
                calls.append(args)
                return mock_proc

            with patch("asyncio.create_subprocess_exec", side_effect=capture_create):
                emit = AsyncMock()
                asyncio.new_event_loop().run_until_complete(hand._ensure_sandbox(emit))

        # Check that --template my-template was passed
        cmd_args = calls[0]
        assert "--template" in cmd_args
        idx = cmd_args.index("--template")
        assert cmd_args[idx + 1] == "my-template"


# ---------------------------------------------------------------------------
# _remove_sandbox (async, mocked subprocess)
# ---------------------------------------------------------------------------


class TestRemoveSandbox:
    def test_skips_if_not_created(self, hand) -> None:
        hand._sandbox_created = False
        emit = AsyncMock()
        asyncio.new_event_loop().run_until_complete(hand._remove_sandbox(emit))
        emit.assert_not_awaited()

    def test_stops_and_removes_sandbox(self, hand, monkeypatch) -> None:
        hand._sandbox_created = True
        monkeypatch.setenv("HELPING_HANDS_DOCKER_SANDBOX_NAME", "test-sb")

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            emit = AsyncMock()
            asyncio.new_event_loop().run_until_complete(hand._remove_sandbox(emit))

        assert hand._sandbox_created is False
