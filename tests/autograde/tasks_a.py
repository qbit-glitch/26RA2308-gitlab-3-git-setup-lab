"""Graders for lab tasks 1 to 4 (8 + 14 + 12 + 16 = 50 marks)."""
from __future__ import annotations

import os
from typing import Optional

from . import configlist, lsparse
from .common import (answer_text, basename, is_global_origin, lines, norm, norm_path, only_line, student_name, valid_email,
                     version_of, version_ok, which_path)
from .context import Ctx
from .framework import Task
from .taskinfo import MARKS, MIN_VERSION, TITLES


def _editor_is_nano(value: Optional[str]) -> bool:
    words = (value or "").split()
    return bool(words) and basename(words[0]).lower() in ("nano", "nano.exe")


def grade_task1(ctx: Ctx) -> Task:
    """Is Git here: the version and where the program is."""
    task = Task(1, TITLES[1], MARKS[1], ctx.repo_mode)
    text = "\n".join(lines(ctx, "1.1"))
    path = which_path(ctx, "1.2")
    expected = "yes" if version_ok(text) else "no"
    other = "no" if expected == "yes" else "yes"
    task.check(2, "1.1 shows a Git version", version_of(text) is not None)
    task.check(1, f"1.1 the version is at least {MIN_VERSION[0]}.{MIN_VERSION[1]}", version_ok(text))
    task.check(2, "1.2 which git prints the path of the git program", path is not None)
    task.check(2, "that path is a file on this computer",
               lambda: path is not None and (os.name == "nt" or ctx.facts.exists(path)), needs_repo=True)
    task.check(1, "ANSWER-1 says whether the version is new enough",
               version_of(text) is not None and lsparse.answer_is(ctx.text, 1, expected) and not lsparse.answer_is(ctx.text, 1, other))
    return task


def grade_task2(ctx: Ctx) -> Task:
    """Who are you: the identity in ~/.gitconfig."""
    task = Task(2, TITLES[2], MARKS[2], ctx.repo_mode)
    name, printed_name, printed_email = student_name(ctx), only_line(ctx, "2.1"), only_line(ctx, "2.2")
    name_ok = bool(name) and printed_name is not None and norm(printed_name) == norm(name)
    email_ok = printed_email is not None and valid_email(printed_email)
    live_name, live_email = ctx.facts.global_value("user.name"), ctx.facts.global_value("user.email")
    task.check(1, "the Name line of outputs.txt is filled in", bool(name))
    task.check(3, "2.1 prints the name you set, the same as the Name line", name_ok)
    task.check(3, "your global settings hold that name",
               lambda: name_ok and live_name is not None and norm(live_name) == norm(name), needs_repo=True)
    task.check(3, "2.2 prints an email address that is yours (not an example)", email_ok)
    task.check(3, "your global settings hold that email",
               lambda: email_ok and live_email is not None and printed_email is not None and live_email.lower() == printed_email.lower(),
               needs_repo=True)
    task.check(1, "the email in your global settings looks like a real address",
               lambda: email_ok and valid_email(live_email or ""), needs_repo=True)
    return task


def grade_task3(ctx: Ctx) -> Task:
    """Defaults: editor, first branch name and pull strategy."""
    task = Task(3, TITLES[3], MARKS[3], ctx.repo_mode)
    editor, branch = only_line(ctx, "3.1"), only_line(ctx, "3.2")
    pull = [norm(line) for line in lines(ctx, "3.3")]
    editor_ok, branch_ok, pull_ok = _editor_is_nano(editor), branch == "main", "pull.rebase=false" in pull
    task.check(2, "3.1 prints the editor you chose", editor_ok)
    task.check(2, "your global settings hold that editor", lambda: editor_ok and _editor_is_nano(ctx.facts.global_value("core.editor")),
               needs_repo=True)
    task.check(2, "3.2 prints the name of the first branch you chose", branch_ok)
    task.check(2, "your global settings hold that first branch name",
               lambda: branch_ok and (ctx.facts.global_value("init.defaultbranch") or "").strip() == "main", needs_repo=True)
    task.check(2, "3.3 shows the pull strategy you set", pull_ok)
    task.check(2, "your global settings hold that pull strategy",
               lambda: pull_ok and (ctx.facts.global_value("pull.rebase") or "").strip().lower() == "false", needs_repo=True)
    return task


def grade_task4(ctx: Ctx) -> Task:
    """Where do the values come from: the listings and the files behind them."""
    task = Task(4, TITLES[4], MARKS[4], ctx.repo_mode)
    name = student_name(ctx)
    plain, origins = configlist.parse(ctx.step("4.1")), configlist.parse(ctx.step("4.2"))
    pasted_email = only_line(ctx, "2.2")
    shown = configlist.last(plain, "user.name"), configlist.last(plain, "user.email")
    list_ok = bool(name) and shown[0] is not None and norm(shown[0]) == norm(name) and valid_email(shown[1] or "")
    origin = configlist.origin_of(origins, "user.name")
    local_lines = [e for e in origins if e.origin is not None and norm_path(e.origin).endswith(".git/config")]
    origin_ok = is_global_origin(ctx, origin) and bool(local_lines)
    expected_email = pasted_email or ctx.facts.global_value("user.email") or ""
    printed_name, printed_email = only_line(ctx, "4.3"), only_line(ctx, "4.4")
    answer = answer_text(ctx, 3)
    answer = answer[len("file:"):] if answer.lower().startswith("file:") else answer  # the listing shows file:<path>
    task.check(3, "4.1 lists your name and your email among the settings", list_ok)
    task.check(3, "4.2 shows each setting with its file: your settings file, and the settings of this folder", origin_ok)
    task.check(2, "4.3 prints your global name", bool(name) and printed_name is not None and norm(printed_name) == norm(name))
    task.check(2, "4.4 prints the email that is in force here",
               printed_email is not None and valid_email(printed_email) and printed_email.lower() == expected_email.lower())
    task.check(2, "ANSWER-2 is the number of lines that 4.1 printed",
               lsparse.answer_number(ctx.text, 2) == configlist.count(ctx.step("4.1")) != 0)
    task.check(2, "ANSWER-3 is the file that user.name comes from in 4.2",
               bool(answer) and origin is not None and norm_path(answer) == norm_path(origin))
    task.check(2, "the file named in 4.2 is the global settings file of this account",
               lambda: origin_ok and ctx.facts.global_origin("user.name") is not None
               and ctx.facts.same_file(norm_path(origin or ""), ctx.facts.global_origin("user.name") or ""), needs_repo=True)
    return task
