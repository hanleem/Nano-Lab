from collections import Counter
from io import StringIO
import csv
import re

from app.schemas import CompareResult

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9가-힣_]+")


def simple_ocr(filename: str, content: bytes) -> str:
    """MVP placeholder OCR. If utf-8 decodable, return text; else return metadata."""
    try:
        decoded = content.decode("utf-8")
        if decoded.strip():
            return decoded[:12000]
    except UnicodeDecodeError:
        pass
    return f"[OCR_PLACEHOLDER] extracted content from {filename} ({len(content)} bytes)"


def compare_texts(left_text: str, right_text: str) -> CompareResult:
    left_tokens = TOKEN_PATTERN.findall(left_text.lower())
    right_tokens = TOKEN_PATTERN.findall(right_text.lower())

    left_set = set(left_tokens)
    right_set = set(right_tokens)

    union = left_set | right_set
    overlap_score = (len(left_set & right_set) / len(union)) if union else 1.0

    left_counter = Counter(left_tokens)
    right_counter = Counter(right_tokens)

    left_only = sorted([t for t in left_set if t not in right_set], key=lambda t: (-left_counter[t], t))[:20]
    right_only = sorted([t for t in right_set if t not in left_set], key=lambda t: (-right_counter[t], t))[:20]

    return CompareResult(overlap_score=round(overlap_score, 4), left_only=left_only, right_only=right_only)


def requirements_to_csv(rows: list[tuple[int, str, str, str]]) -> str:
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(["id", "title", "detail", "priority"])
    for row in rows:
        writer.writerow(row)
    return out.getvalue()
