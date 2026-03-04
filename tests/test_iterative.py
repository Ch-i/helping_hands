"""Tests for _BasicIterativeHand parsing, extraction, and utility methods."""

from __future__ import annotations

import pytest

from helping_hands.lib.hands.v1.hand.iterative import _BasicIterativeHand

# ---------------------------------------------------------------------------
# _is_satisfied
# ---------------------------------------------------------------------------


class TestIsSatisfied:
    def test_yes(self):
        assert _BasicIterativeHand._is_satisfied("Done.\nSATISFIED: yes") is True

    def test_no(self):
        assert (
            _BasicIterativeHand._is_satisfied("Still working.\nSATISFIED: no") is False
        )

    def test_missing(self):
        assert _BasicIterativeHand._is_satisfied("No marker here.") is False

    def test_case_insensitive(self):
        assert _BasicIterativeHand._is_satisfied("satisfied: YES") is True

    def test_extra_whitespace(self):
        assert _BasicIterativeHand._is_satisfied("SATISFIED:  yes") is True


# ---------------------------------------------------------------------------
# _extract_inline_edits
# ---------------------------------------------------------------------------


class TestExtractInlineEdits:
    def test_single_edit(self):
        content = "@@FILE: src/main.py\n```python\nprint('hello')\n```"
        edits = _BasicIterativeHand._extract_inline_edits(content)
        assert len(edits) == 1
        assert edits[0] == ("src/main.py", "print('hello')")

    def test_multiple_edits(self):
        content = (
            "@@FILE: a.py\n```python\ncode_a\n```\n\n"
            "@@FILE: b.txt\n```text\ncode_b\n```"
        )
        edits = _BasicIterativeHand._extract_inline_edits(content)
        assert len(edits) == 2
        assert edits[0][0] == "a.py"
        assert edits[1][0] == "b.txt"

    def test_no_edits(self):
        assert _BasicIterativeHand._extract_inline_edits("No file blocks here.") == []

    def test_whitespace_in_path(self):
        content = "@@FILE:  src/hello.py \n```python\npass\n```"
        edits = _BasicIterativeHand._extract_inline_edits(content)
        assert len(edits) == 1
        assert edits[0][0] == "src/hello.py"

    def test_multiline_content(self):
        content = "@@FILE: config.yaml\n```yaml\nkey: value\nnested:\n  child: 1\n```"
        edits = _BasicIterativeHand._extract_inline_edits(content)
        assert len(edits) == 1
        assert "nested:" in edits[0][1]


# ---------------------------------------------------------------------------
# _extract_read_requests
# ---------------------------------------------------------------------------


class TestExtractReadRequests:
    def test_explicit_read(self):
        content = "@@READ: src/main.py\n"
        paths = _BasicIterativeHand._extract_read_requests(content)
        assert paths == ["src/main.py"]

    def test_multiple_reads(self):
        content = "@@READ: a.py\n@@READ: b.py\n"
        paths = _BasicIterativeHand._extract_read_requests(content)
        assert paths == ["a.py", "b.py"]

    def test_fallback_pattern(self):
        content = "Please read the file `src/config.py` for me."
        paths = _BasicIterativeHand._extract_read_requests(content)
        assert paths == ["src/config.py"]

    def test_no_requests(self):
        assert _BasicIterativeHand._extract_read_requests("Nothing here.") == []

    def test_explicit_takes_precedence_over_fallback(self):
        content = "@@READ: a.py\nPlease read the file `b.py`."
        paths = _BasicIterativeHand._extract_read_requests(content)
        assert paths == ["a.py"]


# ---------------------------------------------------------------------------
# _extract_tool_requests
# ---------------------------------------------------------------------------


class TestExtractToolRequests:
    def test_valid_tool(self):
        content = '@@TOOL: shell_exec\n```json\n{"command": "ls"}\n```'
        reqs = _BasicIterativeHand._extract_tool_requests(content)
        assert len(reqs) == 1
        name, payload, error = reqs[0]
        assert name == "shell_exec"
        assert payload == {"command": "ls"}
        assert error is None

    def test_invalid_json(self):
        content = "@@TOOL: bad_tool\n```json\n{not valid json}\n```"
        reqs = _BasicIterativeHand._extract_tool_requests(content)
        assert len(reqs) == 1
        assert reqs[0][1] == {}
        assert "invalid JSON" in reqs[0][2]

    def test_non_dict_payload(self):
        content = '@@TOOL: array_tool\n```json\n["a", "b"]\n```'
        reqs = _BasicIterativeHand._extract_tool_requests(content)
        assert len(reqs) == 1
        assert reqs[0][2] == "payload must be a JSON object"

    def test_no_tool_requests(self):
        assert _BasicIterativeHand._extract_tool_requests("No tools.") == []

    def test_multiple_tools(self):
        content = (
            '@@TOOL: a\n```json\n{"x": 1}\n```\n\n@@TOOL: b\n```json\n{"y": 2}\n```'
        )
        reqs = _BasicIterativeHand._extract_tool_requests(content)
        assert len(reqs) == 2
        assert reqs[0][0] == "a"
        assert reqs[1][0] == "b"


# ---------------------------------------------------------------------------
# _parse_str_list
# ---------------------------------------------------------------------------


class TestParseStrList:
    def test_valid_list(self):
        assert _BasicIterativeHand._parse_str_list(
            {"paths": ["a.py", "b.py"]}, key="paths"
        ) == ["a.py", "b.py"]

    def test_missing_key(self):
        assert _BasicIterativeHand._parse_str_list({}, key="paths") == []

    def test_none_value(self):
        assert _BasicIterativeHand._parse_str_list({"paths": None}, key="paths") == []

    def test_non_list_raises(self):
        with pytest.raises(ValueError, match="must be a list"):
            _BasicIterativeHand._parse_str_list({"paths": "single"}, key="paths")

    def test_non_string_items_raise(self):
        with pytest.raises(ValueError, match="must contain only strings"):
            _BasicIterativeHand._parse_str_list({"paths": [1, 2]}, key="paths")


# ---------------------------------------------------------------------------
# _parse_positive_int
# ---------------------------------------------------------------------------


class TestParsePositiveInt:
    def test_valid_int(self):
        assert (
            _BasicIterativeHand._parse_positive_int({"n": 5}, key="n", default=1) == 5
        )

    def test_default(self):
        assert _BasicIterativeHand._parse_positive_int({}, key="n", default=3) == 3

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            _BasicIterativeHand._parse_positive_int({"n": 0}, key="n", default=1)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            _BasicIterativeHand._parse_positive_int({"n": -1}, key="n", default=1)

    def test_bool_raises(self):
        with pytest.raises(ValueError, match="must be an integer"):
            _BasicIterativeHand._parse_positive_int({"n": True}, key="n", default=1)

    def test_string_raises(self):
        with pytest.raises(ValueError, match="must be an integer"):
            _BasicIterativeHand._parse_positive_int({"n": "5"}, key="n", default=1)


# ---------------------------------------------------------------------------
# _parse_optional_str
# ---------------------------------------------------------------------------


class TestParseOptionalStr:
    def test_valid_string(self):
        assert (
            _BasicIterativeHand._parse_optional_str({"msg": "hello"}, key="msg")
            == "hello"
        )

    def test_none_returns_none(self):
        assert _BasicIterativeHand._parse_optional_str({}, key="msg") is None

    def test_empty_string_returns_none(self):
        assert _BasicIterativeHand._parse_optional_str({"msg": "  "}, key="msg") is None

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            _BasicIterativeHand._parse_optional_str({"msg": 123}, key="msg")


# ---------------------------------------------------------------------------
# _truncate_tool_output
# ---------------------------------------------------------------------------


class TestTruncateToolOutput:
    def test_short_text_unchanged(self):
        text, truncated = _BasicIterativeHand._truncate_tool_output("short")
        assert text == "short"
        assert truncated is False

    def test_long_text_truncated(self):
        long_text = "x" * (_BasicIterativeHand._MAX_TOOL_OUTPUT_CHARS + 100)
        text, truncated = _BasicIterativeHand._truncate_tool_output(long_text)
        assert len(text) == _BasicIterativeHand._MAX_TOOL_OUTPUT_CHARS
        assert truncated is True

    def test_exact_limit_not_truncated(self):
        exact = "y" * _BasicIterativeHand._MAX_TOOL_OUTPUT_CHARS
        text, truncated = _BasicIterativeHand._truncate_tool_output(exact)
        assert text == exact
        assert truncated is False


# ---------------------------------------------------------------------------
# _merge_iteration_summary
# ---------------------------------------------------------------------------


class TestMergeIterationSummary:
    def test_no_feedback(self):
        result = _BasicIterativeHand._merge_iteration_summary("content", "")
        assert result == "content"

    def test_with_feedback(self):
        result = _BasicIterativeHand._merge_iteration_summary("content", "tool output")
        assert "content" in result
        assert "Tool results:" in result
        assert "tool output" in result
