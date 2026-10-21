"""Last step of every XML generator here: literal label text goes to strings.po (localize.py)."""
from pathlib import Path

from localize import Po, localize

_PO = Po(Path(__file__).resolve().parents[1] / "language" / "resource.language.en_gb" / "strings.po")


def finish_xml(text: str) -> str:
    out = localize(text, _PO)
    _PO.save()
    return out
