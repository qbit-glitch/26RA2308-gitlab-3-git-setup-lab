"""Graders for lab tasks 5 to 7 (14 + 16 + 20 = 50 marks)."""
from __future__ import annotations

import os
import re
from typing import Dict

from . import configlist, loglines, lsparse, published, sshkey
from .common import answer_text, is_global_origin, lines, norm, norm_path, only_line, valid_email
from .context import Ctx
from .framework import Task
from .taskinfo import ALIAS_LG, LOCAL_EMAIL, MARKS, TITLES

GREETING_RE = re.compile(r"Hi (\S+?)! You've successfully authenticated, but GitHub does not provide shell access\.")
GITHUB_NAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")


def _global_email(ctx: Ctx) -> str:
    """The email the student set in Task 2: what they pasted, else what their global settings hold."""
    return (only_line(ctx, "2.2") or ctx.facts.global_value("user.email") or "").lower()


def grade_task5(ctx: Ctx) -> Task:
    """Local beats global: a setting of this folder overrides the account's."""
    task = Task(5, TITLES[5], MARKS[5], ctx.repo_mode)
    expected = _global_email(ctx)
    printed = [only_line(ctx, step) for step in ("5.1", "5.2", "5.4")]
    local_ok = printed[0] == LOCAL_EMAIL
    global_ok = printed[1] is not None and valid_email(printed[1]) and printed[1].lower() == expected != LOCAL_EMAIL
    both = [e for e in configlist.parse(ctx.step("5.3")) if e.key == "user.email" and e.origin is not None]
    origins_ok = (any(is_global_origin(ctx, e.origin) for e in both)
                  and any(norm_path(e.origin or "").endswith(".git/config") for e in both))
    undone_ok = printed[2] is not None and printed[2].lower() == expected and expected != ""
    answer = answer_text(ctx, 4).lower()
    task.check(3, "5.1 prints the local email: in this folder it wins", local_ok)
    task.check(3, "5.2 prints your global email, which is another one", global_ok)
    task.check(3, "5.3 lists user.email twice: once from your settings file, once from this folder's settings", origins_ok)
    task.check(1, "ANSWER-4 says which one wins in this folder", "local" in answer and "global" not in answer)
    task.check(2, "5.4 prints your global email again", undone_ok)
    task.check(2, "this folder's settings no longer hold an email",
               lambda: undone_ok and ctx.facts.local_has("user.email") is False, needs_repo=True)
    return task


def _aliases(ctx: Ctx, step: str) -> Dict[str, str]:
    """`alias.name value` lines of `git config --get-regexp alias`."""
    found: Dict[str, str] = {}
    for line in lines(ctx, step):
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0].lower().startswith("alias."):
            found[parts[0].lower()] = parts[1].strip()
    return found


def _log_ok(ctx: Ctx) -> bool:
    commits = loglines.parse(ctx.step("6.4"))
    return (len(commits) == len(published.SUBJECTS) and sorted(s for _, s in commits) == sorted(published.SUBJECTS)
            and all(published.HISTORY[s].startswith(h) for h, s in commits if s in published.HISTORY))


def grade_task6(ctx: Ctx) -> Task:
    """Shortcuts: aliases, one of them typed in nano, and used."""
    task = Task(6, TITLES[6], MARKS[6], ctx.repo_mode)
    first, second = _aliases(ctx, "6.1"), _aliases(ctx, "6.2")
    first_ok = first.get("alias.st") == "status" and first.get("alias.lg") == ALIAS_LG
    second_ok = second.get("alias.ci") == "commit" and second.get("alias.st") == "status" and second.get("alias.lg") == ALIAS_LG
    status = [line.lower() for line in lines(ctx, "6.3")]
    status_ok = "on branch main" in [line for line in status if line.startswith("on branch")] and any(
        "working tree clean" in line or "nothing to commit" in line for line in status)
    task.check(3, "6.1 lists the two aliases you made", first_ok)
    task.check(3, "your global settings hold those two aliases",
               lambda: first_ok and ctx.facts.global_value("alias.st") == "status" and ctx.facts.global_value("alias.lg") == ALIAS_LG,
               needs_repo=True)
    task.check(2, "6.2 lists the third alias, typed in nano, with the other two", second_ok)
    task.check(2, "your global settings hold the third alias", lambda: second_ok and ctx.facts.global_value("alias.ci") == "commit",
               needs_repo=True)
    task.check(2, "6.3 the first alias shows the state of this folder", status_ok)
    task.check(3, "6.4 the second alias lists the history of the lab: every commit, with its own hash", _log_ok(ctx))
    task.check(1, "ANSWER-5 is the subject of the newest commit", norm(answer_text(ctx, 5)) == norm(published.LAB_SUBJECT))
    return task


def grade_task7(ctx: Ctx) -> Task:
    """SSH key: a key pair on this computer, its fingerprint, and the greeting of GitHub."""
    task = Task(7, TITLES[7], MARKS[7], ctx.repo_mode)
    made = "\n".join(lines(ctx, "7.1"))
    made_ok = ("Your public key has been saved in" in made and sshkey.parse_fingerprint_line(made) is not None) or "already exists" in made
    pasted_key = sshkey.parse_public_key(ctx.step("7.2"))
    pasted_print = sshkey.parse_fingerprint_line(ctx.step("7.3"))
    live = ctx.facts.pub_key()
    print_ok = live is not None and pasted_print == live.fingerprint
    key_ok = pasted_key is not None and live is not None and (pasted_key.kind, pasted_key.blob) == (live.kind, live.blob)
    wanted = (live.fingerprint if live is not None and ctx.repo_mode else pasted_print or "")[7:15]
    greeting = GREETING_RE.search(" ".join(" ".join(lines(ctx, "7.4")).split()))
    user = greeting.group(1) if greeting else ""
    mode = ctx.facts.private_key_mode()
    task.check(2, "7.1 made the key pair (or found that one exists)", made_ok)
    task.check(4, "7.2 prints the public key that is in ~/.ssh/id_ed25519.pub", lambda: key_ok, needs_repo=True)
    task.check(2, "~/.ssh/id_ed25519.pub is an ed25519 public key", lambda: print_ok and live is not None and live.is_ed25519,
               needs_repo=True)
    task.check(2, "the private key exists and only you can read it",
               lambda: print_ok and mode is not None and (os.name == "nt" or mode & 0o077 == 0), needs_repo=True)
    task.check(4, "7.3 prints the fingerprint of the key on this computer", lambda: print_ok, needs_repo=True)
    task.check(2, "ANSWER-6 is the start of that fingerprint",
               len(wanted) == 8 and answer_text(ctx, 6) == wanted)
    task.check(3, "7.4 shows GitHub greeting you by your user name", bool(greeting) and bool(GITHUB_NAME_RE.match(user)))
    task.check(1, "ANSWER-7 is that user name", bool(user) and answer_text(ctx, 7).lower() == user.lower())
    return task
