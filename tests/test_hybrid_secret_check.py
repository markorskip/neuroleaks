import pytest
from neuroleaks.hybrid_secret_check import regex_match, ml_score

# ✅ Safe lines that should not trigger
SAFE_LINES = [
    "def add(x, y): return x + y",
    "print('Hello world')",
    "user_id = 12345"
]

# ❌ Suspicious lines (secrets or high-risk patterns)
SUSPICIOUS_LINES = [
    "aws_secret_access_key = 'AKIAIOSFODNN7EXAMPLE'",
    "token = 'ghp_123456789abcdef'",
    "api_key = 'AIzaSyD1234567890abcdefg'",
    "password = 'hunter2'",
    "jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'"
]

def test_regex_catches_known_secrets():
    for line in SUSPICIOUS_LINES:
        assert regex_match(line) is not None, f"Regex missed: {line}"

def test_regex_skips_safe_lines():
    for line in SAFE_LINES:
        assert regex_match(line) is None, f"False positive: {line}"

def test_ml_scores_known_secrets():
    for line in SUSPICIOUS_LINES:
        prob = ml_score(line)
        assert prob > 0.5, f"ML missed secret (score too low): {line} ({prob:.2f})"

def test_ml_scores_safe_lines_low():
    for line in SAFE_LINES:
        prob = ml_score(line)
        assert prob < 0.5, f"ML false positive on safe line: {line} ({prob:.2f})"
