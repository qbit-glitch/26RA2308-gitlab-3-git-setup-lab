"""Readers for pasted `ls` listings, `pwd` paths and typed answers.

Only things that are the same on every machine are read: the type character, the owner permission triplet, the
size and the name. Dates, groups, link counts, `total` lines and group/other permission bits are ignored.
Everything is token based and linear in the length of the pasted text, and every line is cut to MAX_LINE
characters first, so a hostile pasted line cannot make the grader slow.
"""
from __future__ import annotations

import re
from typing import List, NamedTuple, Optional

from . import textutil

MAX_LINE = 500
SIGILS = "$%#>"
SUFFIXES = "/*@=|"  # what `ls -F` (the default alias in Git Bash) adds to directories, executables, links...
MODE_RE = re.compile(r"^[-dlcbps][-rwxsStT]{9}[@+.]?$")
TIME_RE = re.compile(r"^(?:\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?|\d{4})$")
MONTH_RE = re.compile(r"^[A-Za-z]{3,5}\.?$")
DAY_RE = re.compile(r"^\d{1,2}$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
STEP_REF_RE = re.compile(r"\b\d\.\d\b")


class LsRow(NamedTuple):
    """One row of `ls -l` / `ls -la` output."""

    kind: str     # "-" file, "d" directory, "l" symlink
    owner: str    # the owner's permission triplet, e.g. "rw-"
    size: int     # bytes (meaningless for a directory)
    name: str
    account: str  # the first word of the owner/group part (the owner's account name)


def _lines(text: str) -> List[str]:
    return [line[:MAX_LINE] for line in textutil.normalise(text).split("\n")]


def is_prompt_line(line: str) -> bool:
    """A shell prompt, with or without the command typed after it ($, %, #, > ; user@host forms; Git Bash's two lines)."""
    tokens = line.split()
    if not tokens:
        return False
    for token in tokens[:4]:
        if len(token) == 1 and token in SIGILS:
            return True
        if token[-1] in SIGILS and any(c in token for c in "@:/~]"):
            return True
    return "@" in tokens[0] and len(tokens) > 1 and tokens[1].startswith(("MINGW", "MSYS", "UCRT", "CLANG"))


def _date_length(tokens: List[str], at: int) -> int:
    """How many tokens a date starting at 'at' takes (0 if there is none): 'Oct 17 12:00', '17 Oct 2025', '2026-10-17 12:00'."""
    part = tokens[at:at + 3]
    if len(part) >= 2 and ISO_RE.match(part[0]) and TIME_RE.match(part[1]):
        return 2
    if len(part) == 3 and TIME_RE.match(part[2]):
        if MONTH_RE.match(part[0]) and DAY_RE.match(part[1]):
            return 3
        if DAY_RE.match(part[0]) and MONTH_RE.match(part[1]):
            return 3
    return 0


def _clean(name: str) -> str:
    """A listed name without `ls -F` marks and without a leading folder (`ls -l dir/file` prints the path as typed)."""
    while len(name) > 1 and name[-1] in SUFFIXES:
        name = name[:-1]
    return name.rsplit("/", 1)[-1] or name


def parse_ls_rows(text: str) -> List[LsRow]:
    """The long-format rows in 'text'. The size is the number just before the date; whatever lies between the link
    count and the size is the owner and group, which may contain spaces ('domain users')."""
    rows: List[LsRow] = []
    for line in _lines(text):
        tokens = line.split()
        if len(tokens) < 6 or not MODE_RE.match(tokens[0]):
            continue
        for at in range(3, len(tokens)):
            length = _date_length(tokens, at) if tokens[at - 1].isdigit() else 0
            if length:
                size, who, rest = int(tokens[at - 1]), tokens[2:at - 1], tokens[at + length:]
                break
        else:  # an unfamiliar date: assume the usual layout (mode links owner group size date... name)
            if not tokens[4].isdigit():
                continue
            size, who, rest = int(tokens[4]), tokens[2:4], tokens[-1:]
        if "->" in rest:
            rest = rest[:rest.index("->")]
        if rest and who:
            rows.append(LsRow(tokens[0][0], tokens[0][1:4], size, _clean(" ".join(rest)), who[0]))
    return rows


def plain_names(text: str) -> List[str]:
    """The names in a short `ls` / `ls -a` listing (any number of columns), ignoring echoed prompt lines."""
    names: List[str] = []
    for line in _lines(text):
        if line.strip() and not is_prompt_line(line):
            names.extend(_clean(token) for token in line.split())
    return names


def paths(text: str) -> List[str]:
    """Every absolute path printed in 'text' (a line starting with /, ~/ or a drive letter), backslashes turned to /.
    zsh prints `cd -` as ~/folder, so a leading ~ counts."""
    found: List[str] = []
    for line in _lines(text):
        stripped = line.strip().strip("\"'")
        if is_prompt_line(stripped):
            continue
        if stripped.startswith(("/", "~/")) or stripped == "~" or DRIVE_RE.match(stripped):
            path = stripped.replace("\\", "/")
            found.append(path if path == "/" else path.rstrip("/"))
    return found


def path_ends(text: str, suffix: str, index: int = 0) -> bool:
    """Does the index-th path in 'text' end with 'suffix' (compared whole-component, so -old does not match)?"""
    found = paths(text)
    if index >= len(found):
        return False
    return found[index].endswith("/" + suffix.strip("/"))


def answer_is(text: str, number: int, expected: str) -> bool:
    """Does the student's ANSWER-<number> contain 'expected' as a whole word? ('456 bytes' yes, '4560' no)."""
    raw = textutil.get_answer(text, number).lower().replace("`", "")[:MAX_LINE]
    if not raw:
        return False
    pattern = r"(?<![\w.-])" + re.escape(expected.lower()) + r"(?![\w-])"
    return re.search(pattern, raw) is not None


def answer_number(text: str, number: int) -> Optional[int]:
    """The first whole number in the student's ANSWER-<number> that is not a step number like 4.3, or None."""
    raw = STEP_REF_RE.sub(" ", textutil.get_answer(text, number)[:MAX_LINE])
    match = re.search(r"\d+", raw)
    return int(match.group(0)) if match else None
