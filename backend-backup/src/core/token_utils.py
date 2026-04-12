import math

from . import cfg


def estimate_tokens_from_text(text: str) -> int:
    words = text.split()
    return math.ceil(len(words) * cfg.TOKENS_PER_WORD)


def truncate_head_tail(text: str, allowed_tokens: int) -> tuple[str, bool]:
    if estimate_tokens_from_text(text) <= allowed_tokens:
        return text, False

    words = text.split()
    total_words = len(words)
    allowed_words = math.floor(allowed_tokens / cfg.TOKENS_PER_WORD)

    if allowed_words < 2:
        # Can't truncate meaningfully, return first word
        truncated = " ".join(words[:1])
        return truncated, True

    # Head and tail
    head_words = allowed_words // 2
    tail_words = allowed_words - head_words
    truncated = " ".join(words[:head_words] + words[-tail_words:])
    return truncated, True
