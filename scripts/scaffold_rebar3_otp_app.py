#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "rebar3-otp-template"
PLACEHOLDER = "myapp"


def normalize_app_name(raw: str) -> str:
    candidate = raw.strip().lower().replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", candidate):
        raise ValueError(
            "application name must start with a lowercase letter and contain only lowercase letters, digits, underscores, or hyphens"
        )
    return candidate


def replace_text(path: Path, app_name: str) -> None:
    content = path.read_text()
    path.write_text(content.replace(PLACEHOLDER, app_name))


def rename_paths(root: Path, app_name: str) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if PLACEHOLDER in path.name:
            path.rename(path.with_name(path.name.replace(PLACEHOLDER, app_name)))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 scaffold_rebar3_otp_app.py <app_name> <destination>")
        return 1

    app_name = normalize_app_name(argv[1])
    destination = Path(argv[2]).expanduser().resolve()

    if destination.exists():
        print(f"destination already exists: {destination}")
        return 1

    shutil.copytree(TEMPLATE_DIR, destination)

    for file_path in destination.rglob("*"):
        if file_path.is_file():
            replace_text(file_path, app_name)

    rename_paths(destination, app_name)

    print(f"created OTP app template at {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
