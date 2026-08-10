"""Detects pasted output that does not belong to this computer and this clone."""
from __future__ import annotations

import os
from typing import List

from . import configlist, sshkey
from .textutil import header_field, safe_text
from .common import lines, norm, norm_path, student_name, which_path
from .context import Ctx
from .taskinfo import PLACEHOLDER_NAMES

CAST = {"asha verma", "ben carter", "chitra rao", "course staff"}
MAX_WARNINGS = 5


def _is_account_file(ctx: Ctx, path: str) -> bool:
    """Is the path one of the global settings files of this account (the same file, or the same path as written)?"""
    wanted = norm_path(path)
    for known in ctx.facts.global_files():
        if ctx.facts.same_file(wanted, known) or norm_path(known).lower() == wanted.lower():
            return True
    return False


def integrity_warnings(ctx: Ctx) -> List[str]:
    """Human-readable warnings; an empty list means the pasted text looks like it came from this computer."""
    if not ctx.repo_mode:
        return []
    warnings: List[str] = []
    name, written = student_name(ctx), safe_text(header_field(ctx.text, "Name"))
    if not written:
        warnings.append("the Name line at the top of submission/outputs.txt is blank")
    elif not name:
        warnings.append(f"the Name line holds the example name '{written}' of the handout; put your own name there")
    elif name.lower() in CAST:
        warnings.append(f"the Name line holds a teammate's name ('{name}'); put your own name there")
    for step, label, key_name in (("2.1", "name", "user.name"), ("2.2", "email", "user.email")):
        if lines(ctx, step) and ctx.facts.global_value(key_name) is None:
            warnings.append(f"step {step} printed a {label}, but the global settings of this account hold no {key_name}; "
                            "the outputs were not produced in this account")
    key, pasted = ctx.facts.pub_key(), sshkey.parse_fingerprint_line(ctx.step("7.3"))
    if key is None and (sshkey.parse_public_key(ctx.step("7.2")) is not None or pasted is not None):
        warnings.append("steps 7.2 and 7.3 show a key, but this account has no ~/.ssh/id_ed25519.pub; "
                        "the outputs were not produced in this account")
    if key is not None and pasted is not None and pasted != key.fingerprint:
        warnings.append("the key fingerprint pasted for step 7.3 is not the fingerprint of the key on this computer; "
                        "the outputs were not produced on this computer")
    origin = configlist.origin_of(configlist.parse(ctx.step("4.2")), "user.name")
    if origin is not None and not _is_account_file(ctx, origin):
        warnings.append(f"step 4.2 says user.name comes from {origin}, which is not a global settings file of this account")
    path = which_path(ctx, "1.2")
    if path is not None and os.name != "nt" and not ctx.facts.exists(path):
        warnings.append(f"the path pasted for step 1.2 ({path}) does not exist on this computer")
    return warnings[:MAX_WARNINGS]
