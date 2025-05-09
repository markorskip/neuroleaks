import sys
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from git import Repo

# === CONFIG ===
MODEL_NAME = "microsoft/codebert-base"
THRESHOLD = 0.8
MAX_LEN = 512

# === REGEX PATTERNS ===
REGEX_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",                      # AWS Access Key
    r"(?i)aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]?",
    r"(?i)(api|secret|token|key|passwd|password)[\s:=]+['\"].{6,}['\"]",
    r"ghp_[A-Za-z0-9]{36}",                   # GitHub token
    r"(?i)(jwt|bearer)\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+"
]

# === LOAD MODEL ===
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def get_staged_lines():
    repo = Repo(".")
    diff = repo.git.diff("--cached", unified=0)
    return [
        (i + 1, line[1:])
        for i, line in enumerate(diff.split("\n"))
        if line.startswith("+") and not line.startswith("+++")
    ]

def regex_match(line):
    for pattern in REGEX_PATTERNS:
        if re.search(pattern, line):
            return pattern
    return None

def ml_score(line):
    inputs = tokenizer(line, return_tensors="pt", truncation=True, max_length=MAX_LEN)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=1)
    return probs[0][1].item()

def main():
    lines = get_staged_lines()
    regex_hits = []
    ml_hits = []

    for lineno, line in lines:
        pattern = regex_match(line)
        if pattern:
            regex_hits.append((lineno, line.strip(), pattern))
            continue  # Already flagged by regex, skip ML check

        prob = ml_score(line)
        if prob > THRESHOLD:
            ml_hits.append((lineno, line.strip(), prob))

    if regex_hits or ml_hits:
        print("❌ Potential secrets detected:")
        for lineno, line, pattern in regex_hits:
            print(f"  [REGEX] Line {lineno}: '{line}' matched `{pattern}`")
        for lineno, line, prob in ml_hits:
            print(f"  [ML]    Line {lineno}: '{line}' (risk score: {prob:.2f})")
        sys.exit(1)
    else:
        print("✅ No secrets detected by regex or ML.")
        sys.exit(0)

if __name__ == "__main__":
    main()
