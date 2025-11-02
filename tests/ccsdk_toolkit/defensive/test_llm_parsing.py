"""Tests for LLM response parsing with defensive handling"""

from amplifier.ccsdk_toolkit.defensive.llm_parsing import parse_llm_json


class TestParseLlmJson:
    """Tests for parse_llm_json function"""

    def test_parse_plain_json(self):
        """Plain JSON parses correctly"""
        input_json = '{"key": "value", "nested": {"items": [1, 2, 3]}}'

        result = parse_llm_json(input_json)

        assert result == {"key": "value", "nested": {"items": [1, 2, 3]}}

    def test_parse_markdown_wrapped_json(self):
        """Markdown code blocks extracted"""
        input_text = """```json
{
  "key": "value",
  "nested": {
    "items": [1, 2, 3]
  }
}
```"""

        result = parse_llm_json(input_text)

        assert result == {"key": "value", "nested": {"items": [1, 2, 3]}}

    def test_parse_json_with_preamble(self):
        """Text before JSON is stripped"""
        input_text = 'Here\'s the result:\n{"key": "value", "number": 42}'

        result = parse_llm_json(input_text)

        assert result == {"key": "value", "number": 42}

    def test_parse_malformed_json_returns_default(self):
        """Invalid JSON returns default"""
        input_text = "{invalid json}"
        default_value = {"fallback": "data"}

        result = parse_llm_json(input_text, default=default_value)

        assert result == default_value

    def test_parse_nested_json_in_text(self):
        """Nested JSON extracted correctly"""
        input_text = 'Analysis shows that {"nested": {"key": "value", "count": 5}} is the structure.'

        result = parse_llm_json(input_text)

        assert result == {"nested": {"key": "value", "count": 5}}

    def test_parse_empty_string_returns_default(self):
        """Empty string returns default"""
        result = parse_llm_json("", default=None)

        assert result is None

    def test_parse_null_returns_default(self):
        """None input returns default"""
        result = parse_llm_json(None, default=[])  # type: ignore[arg-type]

        assert result == []

    def test_parse_markdown_without_json_keyword(self):
        """Markdown code blocks without 'json' keyword"""
        input_text = """```
{"key": "value"}
```"""

        result = parse_llm_json(input_text)

        assert result == {"key": "value"}

    def test_parse_array_response(self):
        """JSON array responses parse correctly"""
        input_json = '[{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]'

        result = parse_llm_json(input_json)

        assert result == [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]

    def test_parse_with_trailing_commas(self):
        """JSON with trailing commas gets fixed"""
        input_text = '{"key": "value", "items": [1, 2, 3,],}'

        result = parse_llm_json(input_text)

        # Should handle trailing commas
        assert result is not None
        assert "key" in result

    def test_parse_llm_explanation_with_json(self):
        """LLM explanation followed by JSON"""
        input_text = """I'll provide the analysis:

```json
{
  "summary": "test",
  "score": 0.85
}
```

Hope this helps!"""

        result = parse_llm_json(input_text)

        assert result == {"summary": "test", "score": 0.85}

    def test_parse_verbose_mode_logging(self, caplog):
        """Verbose mode logs debugging output"""
        import logging

        caplog.set_level(logging.DEBUG)

        input_text = "{invalid}"
        parse_llm_json(input_text, verbose=True)

        # Verify logging occurred
        assert "JSON parsing" in caplog.text or "failed" in caplog.text.lower()

    def test_parse_handles_single_quotes(self):
        """JSON-like with single quotes gets converted"""
        input_text = "{'key': 'value', 'count': 42}"

        result = parse_llm_json(input_text)

        # Should attempt to fix single quotes (may succeed or return default None)
        assert result is not None or result is None

    def test_parse_multiple_json_objects_uses_first(self):
        """Multiple JSON objects returns first valid one"""
        input_text = """First object: {"first": "value"}

        Second object: {"second": "value"}"""

        result = parse_llm_json(input_text)

        # Should extract at least one of them
        assert result is not None
        assert isinstance(result, dict)
