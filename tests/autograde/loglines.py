"""Reads what `git log --oneline --graph --decorate --all` printed, as a student pastes it: one (hash, subject) per commit."""
from __future__ import annotations

import re
from typing import List, Tuple

from .textutil import ANSI_RE

MAX_LINE = 500
LOG_RE = re.compile(r"^[ *|/\\_.-]*([0-9a-f]{7,40})\s+(?:\(([^)]*)\)\s+)?(\S.*)$")


def parse(text: str) -> List[Tuple[str, str]]:
    """(abbreviated hash, subject) of every commit line, in the order printed (newest first). Graph drawing, decorations,
    prompts and pager marks are not commits."""
    commits: List[Tuple[str, str]] = []
    for raw in ANSI_RE.sub("", text).split("\n"):
        match = LOG_RE.match(raw[:MAX_LINE].rstrip())
        if match:
            commits.append((match.group(1), match.group(3).strip()))
    return commits
