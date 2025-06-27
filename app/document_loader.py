from pathlib import Path
from typing import List, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Any markdown or csv file gets loaded.  Update suffixes if you add PDFs later.
LOAD_SUFFIXES = {".md", ".csv", ".txt"}

def department_from_path(fp: Path) -> str:
    """
    Determine the department tag for a file.
    • If you've nested docs as data/finance/…, we'll take the parent folder name.
    • Fallback to 'general'.
    """
    parent_name = fp.parent.name.lower()
    if parent_name in {"finance", "hr", "engineering", "marketing", "general"}:
        return parent_name
    return "general"

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Naive overlap splitter so the agent sees context edges.
    Feel free to swap for tiktoken or LangChain TextSplitter later.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def load_all() -> List[Tuple[str, dict]]:
    """
    Walk data/ recursively and return [(chunk, metadata), …]
    metadata = {"department": <str>, "source": <filename>}
    """
    output = []
    for fp in DATA_DIR.rglob("*"):
        if fp.suffix.lower() not in LOAD_SUFFIXES or not fp.is_file():
            continue

        dept = department_from_path(fp)
        text = fp.read_text(encoding="utf-8", errors="ignore")
        for chunk in chunk_text(text):
            meta = {"department": dept, "source": fp.name}
            output.append((chunk, meta))
    return output
