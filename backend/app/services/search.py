def rank_word_results(query: str, candidates: list[dict]) -> list[dict]:
    q = query.lower().strip()
    def score(item):
        word = item.get("word", "").lower()
        if word == q: return 100
        if word.startswith(q): return 80
        if q in word: return 60
        return item.get("similarity", 0)
    return sorted(candidates, key=score, reverse=True)
