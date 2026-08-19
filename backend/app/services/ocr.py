from pathlib import Path

def recognize_handwriting_placeholder(path: str) -> str:
    sidecar = Path(path).with_suffix(".txt")
    if sidecar.exists():
        return sidecar.read_text(encoding="utf-8")
    return ""
