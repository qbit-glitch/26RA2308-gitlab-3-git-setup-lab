"""Small readers and checks that several task graders share."""
from __future__ import annotations

import os
import re
from typing import List, Optional, Tuple

from .context import Ctx
from .taskinfo import MIN_VERSION, PLACEHOLDER_DOMAINS, PLACEHOLDER_EMAILS, PLACEHOLDER_LOCALS, PLACEHOLDER_NAMES
from .textutil import get_answer, header_field, safe_text

EMAIL_RE = re.compile(r"^[^@\s\"'<>()\[\],;:\\]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
VERSION_RE = re.compile(r"git version (\d+)\.(\d+)")
WHICH_RE = re.compile(r"^(?:/|[A-Za-z]:[\\/]).*\bgit(?:\.exe)?$", re.IGNORECASE)
MAX_LINE = 500


def norm(text: str) -> str:
    """Case and blanks ignored: a name is the same name however it was spaced."""
    return " ".join(text.split()).casefold()


def student_name(ctx: Ctx) -> str:
    """The Name line of outputs.txt, safe to print; the example name of the handout is no name."""
    name = safe_text(header_field(ctx.text, "Name"))
    return "" if norm(name) in PLACEHOLDER_NAMES else name


def lines(ctx: Ctx, step: str) -> List[str]:
    """The non-blank lines pasted for a step (prompts and the typed command are already gone)."""
    return [line[:MAX_LINE].strip() for line in ctx.step(step).split("\n") if line.strip()]


def only_line(ctx: Ctx, step: str) -> Optional[str]:
    """The one line a step printed, or None if it printed nothing or more than one line."""
    found = lines(ctx, step)
    return found[0] if len(found) == 1 else None


def valid_email(value: str) -> bool:
    """An address that can be someone's: well formed, and not an example from the manual or the handout."""
    value = value.strip()
    if not EMAIL_RE.match(value) or value.lower() in PLACEHOLDER_EMAILS:
        return False
    local, _, domain = value.lower().rpartition("@")
    return local not in PLACEHOLDER_LOCALS and domain not in PLACEHOLDER_DOMAINS


def version_of(text: str) -> Optional[Tuple[int, int]]:
    """(major, minor) from the first 'git version X.Y...' line, or None."""
    match = VERSION_RE.search(text)
    return (int(match.group(1)), int(match.group(2))) if match else None


def version_ok(text: str) -> bool:
    found = version_of(text)
    return found is not None and found >= MIN_VERSION


def which_path(ctx: Ctx, step: str) -> Optional[str]:
    """The path `which git` printed (the first line that looks like the path of the git program), or None."""
    for line in lines(ctx, step):
        if WHICH_RE.match(line):
            return line
    return None


def answer_text(ctx: Ctx, number: int) -> str:
    """The student's ANSWER-<number>, with quotes and back ticks taken off."""
    return get_answer(ctx.text, number).strip().strip("`'\" ")


def norm_path(path: str) -> str:
    """A path as git prints it, compared across / and \\ and a trailing blank."""
    return path.strip().strip("`'\" ").replace("\\", "/").rstrip("/")


def basename(path: str) -> str:
    return os.path.basename(norm_path(path))


def is_global_origin(ctx: Ctx, origin: Optional[str]) -> bool:
    """Is this the settings file of the account? Its own files by name (~/.gitconfig, the XDG one) or, with a clone,
    any file this account reads as global settings (GIT_CONFIG_GLOBAL may name any file). Not the settings of a folder."""
    if origin is None or norm_path(origin).endswith(".git/config"):
        return False
    if basename(origin) in (".gitconfig", "config"):
        return True
    return any(ctx.facts.same_file(norm_path(origin), known) for known in ctx.facts.global_files())
