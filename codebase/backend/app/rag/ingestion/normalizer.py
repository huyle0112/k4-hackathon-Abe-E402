from __future__ import annotations

import re
import unicodedata


_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_INLINE_WHITESPACE = re.compile(r"[^\S\r\n]+")
_EXCESS_BLANK_LINES = re.compile(r"\n{3,}")
_WORD_OR_PUNCTUATION = re.compile(r"\w+|[^\w\s]", re.UNICODE)
_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)


def normalize_text(text: str) -> str:
    """Normalize PDF/OCR text without removing Vietnamese diacritics."""

    normalized = unicodedata.normalize("NFC", text or "")
    normalized = normalized.replace("\u00ad", "")
    normalized = normalized.replace("\u00a0", " ")
    normalized = normalized.replace("\u200b", "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _CONTROL_CHARACTERS.sub("", normalized)
    normalized = _INLINE_WHITESPACE.sub(" ", normalized)
    normalized = "\n".join(line.strip() for line in normalized.splitlines())
    normalized = _EXCESS_BLANK_LINES.sub("\n\n", normalized)
    return normalized.strip()


def approximate_token_count(text: str) -> int:
    """Return a deterministic token estimate without a provider tokenizer."""

    return len(_WORD_OR_PUNCTUATION.findall(text))


def text_quality_score(text: str) -> float:
    """Estimate whether extracted text is useful enough to avoid OCR."""

    normalized = normalize_text(text)
    if not normalized:
        return 0.0

    visible = [character for character in normalized if not character.isspace()]
    if not visible:
        return 0.0

    letters = len(_LETTER.findall(normalized))
    replacement_characters = normalized.count("\ufffd")
    letter_ratio = letters / len(visible)
    replacement_penalty = min(1.0, replacement_characters / len(visible) * 20)
    length_factor = min(1.0, len(normalized) / 80)
    return max(
        0.0,
        min(1.0, letter_ratio * 0.65 + length_factor * 0.35 - replacement_penalty),
    )


def is_text_usable(text: str, minimum_characters: int = 24) -> bool:
    normalized = normalize_text(text)
    if len(normalized) < minimum_characters:
        return False
    return text_quality_score(normalized) >= 0.42
