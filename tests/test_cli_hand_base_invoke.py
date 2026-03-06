"""Tests for _TwoPhaseCLIHand._invoke_cli_with_cmd subprocess error paths."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stub subclass
# ---------------------------------------------------------------------------
# Import after stdlib/third-party
from helping_hands.lib.hands.v1.hand.cli.base import _TwoPhaseCLIHand


class _Stub(_TwoPhaseCLIHand):
    """Minimal subclass that bypasses __init__ for isolated method tests."""

    _CLI_LABEL = "stub"
    _CLI_DISPLAY_NAME = "Stub CLI"
    _BACKEND_NAME = "stub-backend"
    _COMMAND_ENV_VAR = "STUB_CLI_COMMAND"

    def __init__(self) -> None:
        self._interrupt_event = MagicMock()
        self._interrupt_event.is_set.return_value = False
        self._active_process = None
        self.repo_index = MagicMock()
        self.repo_index.root.resolve.return_value = "/fake/repo"
        self.config = MagicMock()
        self.config.model = "test-model"
        self.config.verbose = False


def _run(coro):
    return asyncio.run(coro)


def _noop_emit():
    async def _emit(chunk: str) -> None:
        pass

    return _emit


def _collecting_emit():
    chunks: list[str] = []

    async def _emit(chunk: str) -> None:
        chunks.append(chunk)

    return _emit, chunks


# ===================================================================
# _invoke_cli_with_cmd — FileNotFoundError without fallback
# ===================================================================


class TestInvokeCmdFileNotFoundNoFallback:
    def test_raises_runtime_error(self) -> None:
        stub = _Stub()
        with (
            patch(
                "asyncio.create_subprocess_exec",
                side_effect=FileNotFoundError("not found"),
            ),
            pytest.raises(RuntimeError, match="command not found"),
        ):
            _run(
                stub._invoke_cli_with_cmd(
                    ["nonexistent-cli", "--arg"],
                    emit=_noop_emit(),
                )
            )

    def test_error_message_includes_command_name(self) -> None:
        stub = _Stub()
        with (
            patch(
                "asyncio.create_subprocess_exec",
                side_effect=FileNotFoundError("not found"),
            ),
            pytest.raises(RuntimeError, match="nonexistent-cli"),
        ):
            _run(
                stub._invoke_cli_with_cmd(
                    ["nonexistent-cli"],
                    emit=_noop_emit(),
                )
            )


# ===================================================================
# _invoke_cli_with_cmd — FileNotFoundError with fallback
# ===================================================================


class TestInvokeCmdFileNotFoundWithFallback:
    def test_retries_with_fallback_command(self) -> None:
        stub = _Stub()
        emit, chunks = _collecting_emit()

        # First call raises FileNotFoundError, second succeeds
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.stdout = AsyncMock()
        mock_process.stdout.read = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=0)

        call_count = 0

        async def _side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise FileNotFoundError("not found")
            return mock_process

        with (
            patch("asyncio.create_subprocess_exec", side_effect=_side_effect),
            patch.object(
                stub,
                "_fallback_command_when_not_found",
                return_value=["alt-cli", "--arg"],
            ),
        ):
            _run(stub._invoke_cli_with_cmd(["orig-cli", "--arg"], emit=emit))

        # Should emit retry message
        assert any("not found" in c and "retrying" in c for c in chunks)

    def test_npx_fallback_emits_npx_message(self) -> None:
        stub = _Stub()
        emit, chunks = _collecting_emit()

        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.stdout = AsyncMock()
        mock_process.stdout.read = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=0)

        call_count = 0

        async def _side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise FileNotFoundError("not found")
            return mock_process

        with (
            patch("asyncio.create_subprocess_exec", side_effect=_side_effect),
            patch.object(
                stub,
                "_fallback_command_when_not_found",
                return_value=["npx", "@some/package", "--arg"],
            ),
        ):
            _run(stub._invoke_cli_with_cmd(["orig-cli", "--arg"], emit=emit))

        # Should emit the npx download message
        assert any("npx fallback" in c for c in chunks)

    def test_fallback_same_as_original_raises(self) -> None:
        stub = _Stub()
        with (
            patch(
                "asyncio.create_subprocess_exec",
                side_effect=FileNotFoundError("not found"),
            ),
            patch.object(
                stub,
                "_fallback_command_when_not_found",
                return_value=["orig-cli", "--arg"],
            ),
            pytest.raises(RuntimeError, match="command not found"),
        ):
            _run(
                stub._invoke_cli_with_cmd(
                    ["orig-cli", "--arg"],
                    emit=_noop_emit(),
                )
            )


# ===================================================================
# _invoke_cli_with_cmd — stdout is None
# ===================================================================


class TestInvokeCmdStdoutNone:
    def test_raises_runtime_error(self) -> None:
        stub = _Stub()
        mock_process = AsyncMock()
        mock_process.stdout = None
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.returncode = None

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_process),
            pytest.raises(RuntimeError, match="did not expose stdout"),
        ):
            _run(
                stub._invoke_cli_with_cmd(
                    ["some-cli"],
                    emit=_noop_emit(),
                )
            )


# ===================================================================
# _invoke_cli_with_cmd — non-zero return code without retry
# ===================================================================


class TestInvokeCmdNonZeroNoRetry:
    def test_raises_runtime_error(self) -> None:
        stub = _Stub()
        mock_stdout = AsyncMock()
        mock_process = AsyncMock()
        mock_process.stdout = mock_stdout
        mock_process.returncode = None
        mock_process.wait = AsyncMock(return_value=1)

        read_count = 0

        async def _read(n):
            nonlocal read_count
            read_count += 1
            if read_count == 1:
                return b"error output here"
            # Signal end of output
            mock_process.returncode = 1
            return b""

        mock_stdout.read = _read

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_process),
            pytest.raises(RuntimeError, match=r"failed.*exit=1"),
        ):
            _run(
                stub._invoke_cli_with_cmd(
                    ["some-cli"],
                    emit=_noop_emit(),
                )
            )


# ===================================================================
# _invoke_cli_with_cmd — non-zero return code with retry
# ===================================================================


class TestInvokeCmdNonZeroWithRetry:
    def test_retries_with_adjusted_command(self) -> None:
        stub = _Stub()
        emit, chunks = _collecting_emit()

        call_count = 0

        def _make_process(*, return_code):
            mock_stdout = MagicMock()
            read_done = False

            async def _read(n):
                nonlocal read_done
                if not read_done:
                    read_done = True
                    return b"output"
                return b""

            mock_stdout.read = _read
            proc = MagicMock()
            proc.stdout = mock_stdout
            proc.returncode = None

            async def _wait():
                proc.returncode = return_code
                return return_code

            proc.wait = _wait
            return proc

        async def _create_subprocess(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _make_process(return_code=1)
            return _make_process(return_code=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=_create_subprocess),
            patch.object(
                stub,
                "_retry_command_after_failure",
                return_value=["some-cli", "--fixed-arg"],
            ),
        ):
            _run(stub._invoke_cli_with_cmd(["some-cli", "--arg"], emit=emit))

        assert any("retrying" in c for c in chunks)
        assert call_count == 2

    def test_retry_same_as_original_raises(self) -> None:
        stub = _Stub()

        async def _read(n):
            return b""

        mock_stdout = MagicMock()
        mock_stdout.read = _read
        proc = MagicMock()
        proc.stdout = mock_stdout
        proc.returncode = None

        async def _wait():
            proc.returncode = 1
            return 1

        proc.wait = _wait

        with (
            patch("asyncio.create_subprocess_exec", return_value=proc),
            patch.object(
                stub,
                "_retry_command_after_failure",
                return_value=["some-cli", "--arg"],
            ),
            pytest.raises(RuntimeError, match=r"failed.*exit=1"),
        ):
            _run(
                stub._invoke_cli_with_cmd(
                    ["some-cli", "--arg"],
                    emit=_noop_emit(),
                )
            )


# ===================================================================
# _invoke_cli_with_cmd — idle timeout
# ===================================================================


class TestInvokeCmdIdleTimeout:
    def test_terminates_on_idle_timeout(self) -> None:
        stub = _Stub()
        # Set very short idle timeout
        with (
            patch.object(stub, "_io_poll_seconds", return_value=0.01),
            patch.object(stub, "_heartbeat_seconds", return_value=0.005),
            patch.object(stub, "_idle_timeout_seconds", return_value=0.02),
        ):
            mock_stdout = MagicMock()

            async def _read_timeout(n):
                await asyncio.sleep(0.1)
                return b""

            mock_stdout.read = _read_timeout
            proc = MagicMock()
            proc.stdout = mock_stdout
            proc.returncode = None

            async def _wait():
                return 0

            proc.wait = _wait

            with (
                patch("asyncio.create_subprocess_exec", return_value=proc),
                patch.object(stub, "_terminate_active_process", new=AsyncMock()),
                pytest.raises(RuntimeError, match="no output"),
            ):
                _run(
                    stub._invoke_cli_with_cmd(
                        ["some-cli"],
                        emit=_noop_emit(),
                    )
                )


# ===================================================================
# _invoke_cli_with_cmd — verbose mode
# ===================================================================


class TestInvokeCmdVerbose:
    def test_verbose_emits_cmd_and_cwd(self) -> None:
        stub = _Stub()
        stub.config.verbose = True
        emit, chunks = _collecting_emit()

        async def _read(n):
            return b""

        mock_stdout = MagicMock()
        mock_stdout.read = _read
        proc = MagicMock()
        proc.stdout = mock_stdout
        proc.returncode = None

        async def _wait():
            proc.returncode = 0
            return 0

        proc.wait = _wait

        with patch("asyncio.create_subprocess_exec", return_value=proc):
            _run(stub._invoke_cli_with_cmd(["some-cli", "--arg"], emit=emit))

        assert any("cmd:" in c for c in chunks)
        assert any("cwd:" in c for c in chunks)
        assert any("finished in" in c for c in chunks)
