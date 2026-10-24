"""Scrub client names out of notebook text before it ever reaches the model.

The list lives OUTSIDE the repo (default ~/.claude-notebook/redact.txt) so names are never committed:

    # one name per line; longest names win, matching is case-insensitive and whole-word
    Acme Corp
    Jane Roe = [Client B lead]

A bare name gets a stable label by position ("[Client A]", "[Client B]" …); `name = label` sets your own.
"""
import os
import re
from pathlib import Path

REDACT_FILE = Path(os.environ.get("CLAUDE_NOTEBOOK_REDACT") or Path.home() / ".claude-notebook" / "redact.txt")


def _label(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return f"[Client {s}]"


def parse(text):
    """redact.txt contents → [(name, label)], longest name first so 'Jane Roe' beats 'Roe'."""
    rules, n = [], 0
    for line in (text or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name, _, label = (p.strip() for p in line.partition("="))
        if not name:
            continue
        if not label:
            label, n = _label(n), n + 1
        rules.append((name, label))
    return sorted(rules, key=lambda r: -len(r[0]))


class Redactor:
    def __init__(self, path=REDACT_FILE):
        self.path = Path(path)
        self._mtime = None
        self._pattern = None
        self._labels = {}

    def _load(self):
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            mtime = None
        if mtime == self._mtime and (self._pattern or mtime is None):
            return
        self._mtime = mtime
        rules = parse(self.path.read_text(encoding="utf-8-sig")) if mtime is not None else []  # -sig: Windows editors add a BOM
        self._labels = {name.lower(): label for name, label in rules}
        # \w-boundaries also catch names glued to punctuation/underscores in filenames ("Acme-01-Filing.pdf")
        alts = "|".join(re.escape(name) for name, _ in rules)
        self._pattern = re.compile(rf"(?<![^\W_])({alts})(?![^\W_])", re.IGNORECASE) if alts else None

    def count(self):
        self._load()
        return len(self._labels)

    def __call__(self, text):
        self._load()
        if not text or not self._pattern:
            return text
        return self._pattern.sub(lambda m: self._labels[m.group(1).lower()], text)
