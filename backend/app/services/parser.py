import re
from dataclasses import dataclass

@dataclass(frozen=True)
class WordItem:
    word: str
    meaning: str

WORD_RE = re.compile(r"([A-Za-z][A-Za-z'\-]*)")
CJK_RE = re.compile(r"[\u4e00-\u9fff].*")

def parse_word_text(text: str) -> list[WordItem]:
    items: list[WordItem] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip().strip(";；,，")
        if not line:
            continue
        word_match = WORD_RE.search(line)
        meaning_match = CJK_RE.search(line)
        if not word_match or not meaning_match:
            continue
        word = word_match.group(1).lower()
        meaning = meaning_match.group(0).strip()
        if word in seen:
            continue
        seen.add(word)
        items.append(WordItem(word=word, meaning=meaning))
    return items
