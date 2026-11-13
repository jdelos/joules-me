#!/usr/bin/env python3
"""Render cover_letter.md to A4 PDF using cover_letter.typ."""
from __future__ import annotations

import argparse
import importlib
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.S)
    if not match:
        return {}, text
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and line.strip():
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"\'')
    return values, match.group(2).lstrip()


def typst_escape(value: str) -> str:
    return (value.replace("\\", "\\\\").replace("#", "\\#")
            .replace("[", "\\[").replace("]", "\\]").replace("@", "\\@"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default="cover_letter.md")
    parser.add_argument("-o", "--output", default="rendered/cover_letter.pdf")
    parser.add_argument("--template", default="cover_letter.typ")
    args = parser.parse_args()

    source = Path(args.source)
    metadata, body = frontmatter(source.read_text(encoding="utf-8"))
    pandoc = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "typst", "--wrap=none"],
        input=body, text=True, capture_output=True, check=True,
    ).stdout.strip()

    full_name = " ".join(filter(None, [metadata.get("name", ""), metadata.get("last_name", "")]))
    town = metadata.get("town", "")
    context = {
        "name": typst_escape(full_name),
        "name_upper": typst_escape(metadata.get("name", "").upper()),
        "name_initial": typst_escape(metadata.get("name", "").upper()[:1]),
        "name_rest": typst_escape(metadata.get("name", "").upper()[1:]),
        "role_upper": typst_escape(metadata.get("role", "").upper()),
        "town": typst_escape(town),
        "country": typst_escape(metadata.get("country", "")),
        "address": typst_escape(metadata.get("address", "")),
        "phone": typst_escape(metadata.get("phone", "")),
        "email": typst_escape(metadata.get("email", "")),
        "date": typst_escape(metadata.get("date", date.today().strftime("%-d %B %Y"))),
        "recipient_name": typst_escape(metadata.get("recipient_name", "")),
        "recipient_company": typst_escape(metadata.get("recipient_company", "")),
        "recipient_address": typst_escape(metadata.get("recipient_address", "")),
        "salutation": typst_escape(metadata.get("salutation", "")),
        "dob": typst_escape(metadata.get("dob", "")),
        "pob": typst_escape(metadata.get("pob", "")),
        "body": pandoc,
    }
    template = Path(args.template).read_text(encoding="utf-8")
    for key, value in context.items():
        template = template.replace("{{" + key + "}}", value)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    typst_source = output.with_suffix(".typ")
    typst_source.write_text(template, encoding="utf-8")

    try:
        typst = importlib.import_module("typst")
    except ImportError:
        # RenderCV already carries a compatible Typst Python binding.
        rendercv = shutil.which("rendercv")
        if rendercv:
            tool_site = Path(rendercv).resolve().parent.parent / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            if tool_site.exists():
                sys.path.insert(0, os.fspath(tool_site))
        try:
            typst = importlib.import_module("typst")
        except ImportError as error:
            raise SystemExit("Typst Python package missing. Install RenderCV first: uv tool install rendercv") from error
    typst.compile(input=str(typst_source), output=str(output), root=str(ROOT))
    print(output)


if __name__ == "__main__":
    main()
