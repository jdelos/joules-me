#!/usr/bin/env python3
"""Render public CV HTML from cv.yaml with PDF-equivalent sb2nov structure."""
from __future__ import annotations

import argparse
import html
import http.client
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
FONT_HOST = "ftp.snt.utwente.nl"
FONT_PATH = "/pub/software/tex/fonts/newcomputermodern/otf"
FONTS = ("NewCM10-Regular.otf", "NewCM10-Bold.otf", "NewCM10-Italic.otf")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec")


def text(value: Any) -> str:
    """Convert RenderCV's inline Typst emphasis to safe HTML."""
    result = html.escape(str(value))
    result = re.sub(
        r"#text\(accent, weight: &quot;bold&quot;\)\[([^]]*)\]",
        r'<strong class="accent">\1</strong>',
        result,
    )
    result = re.sub(r"#text\(black,size:0\.75em \)\[([^]]*)\]", r"\1", result)
    result = re.sub(r"#h\([^)]*\)", " ", result)
    result = re.sub(r"\[#website-icon\]\(([^)]+)\)", r'<a class="icon" href="\1" aria-label="Website">◉</a>', result)
    result = re.sub(r"\[#instagram-icon\]\(([^)]+)\)", r'<a class="icon" href="\1" aria-label="Instagram">◎</a>', result)
    return result


def date_text(value: Any) -> str:
    value = str(value)
    if value == "present":
        return "present"
    match = re.fullmatch(r"(\d{4})-(\d{2})(?:-\d{2})?", value)
    if match:
        month = match.group(2)
        month_names = {f"{index:02d}": name for index, name in enumerate(MONTHS, start=1)}
        return f"{month_names[month]} {match.group(1)}"
    return value


def range_text(entry: dict[str, Any]) -> str:
    if "date" in entry:
        return date_text(entry["date"])
    start, end = entry.get("start_date"), entry.get("end_date")
    if start is None:
        return ""
    return date_text(start) if end is None else f"{date_text(start)} – {date_text(end)}"


def entry_meta(entry: dict[str, Any]) -> str:
    parts = [entry.get("location"), range_text(entry)]
    return "<br>".join(text(item) for item in parts if item)


def highlights(items: list[str] | None) -> str:
    if not items:
        return ""
    return "<ul class=\"highlights\">" + "".join(f"<li>{text(item)}</li>" for item in items) + "</ul>"


def regular_entry(entry: dict[str, Any]) -> str:
    primary = entry.get("position") or entry.get("name")
    secondary = entry.get("company") or entry.get("summary")
    return f'''<article class="entry regular-entry">
  <div class="entry-main"><h3>{text(primary)}</h3>{f'<p class="secondary">{text(secondary)}</p>' if secondary else ''}</div>
  <p class="entry-meta">{entry_meta(entry)}</p>
  {highlights(entry.get("highlights"))}
</article>'''


def education_entry(entry: dict[str, Any]) -> str:
    credential = " ".join(filter(None, (entry.get("degree"), entry.get("area"))))
    return f'''<article class="entry education-entry">
  <div><h3>{text(entry["institution"])}</h3><p class="secondary">{text(credential)}</p></div>
  <p class="entry-meta">{text(entry.get("date", ""))}</p>
</article>'''


def one_line_entry(entry: dict[str, Any]) -> str:
    return f'<p class="one-line"><strong>{text(entry["label"])}:</strong> {text(entry["details"])}</p>'


def section(title: str, entries: list[Any]) -> str:
    if title == "Profile":
        content = f'<p class="profile">{text(entries[0])}</p>'
    elif title == "Education":
        content = "".join(education_entry(entry) for entry in entries)
    elif title in {"Skills", "Certifications and Grants", "Patent portfolio"}:
        content = "".join(one_line_entry(entry) for entry in entries)
    else:
        content = "".join(regular_entry(entry) for entry in entries)
    return f'<section class="cv-section {title.lower().replace(" ", "-")}"><h2>{html.escape(title)}</h2>{content}</section>'


def install_fonts(output: Path) -> None:
    font_dir = output / "fonts"
    font_dir.mkdir(exist_ok=True)
    for font in FONTS:
        target = font_dir / font
        if target.exists() and target.stat().st_size > 100_000:
            continue
        # Host and path fixed in source; no user-controlled URL reaches network client.
        connection = http.client.HTTPSConnection(FONT_HOST, timeout=30)
        try:
            connection.request("GET", f"{FONT_PATH}/{font}")
            response = connection.getresponse()
            if response.status != 200:
                raise RuntimeError(f"Font download failed for {font}: HTTP {response.status}")
            target.write_bytes(response.read())
        finally:
            connection.close()


def render(data: dict[str, Any]) -> str:
    cv = data["cv"]
    headline, _, birth = cv.get("headline", "").partition("#linebreak()")
    # Public version deliberately exposes email only. Source CV remains untouched.
    email = cv.get("email")
    emails = email if isinstance(email, list) else [email] if email else []
    contacts = "".join(f'<a href="mailto:{html.escape(item)}">✉ {html.escape(item)}</a>' for item in emails)
    sections = "\n".join(section(title, entries) for title, entries in cv["sections"].items())
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{html.escape(cv["name"])} — CV</title>
  <link rel="stylesheet" href="cv-html.css">
</head>
<body>
  <main class="cv-page">
    <header class="cv-header">
      <h1>{html.escape(cv["name"])}</h1>
      <p class="headline">{text(headline)}</p>
      <p class="birth">{text(birth)}</p>
      <nav class="contacts">{contacts}</nav>
    </header>
    {sections}
  </main>
</body>
</html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "cv.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "rendered" / "public")
    args = parser.parse_args()

    data = yaml.safe_load(args.source.read_text(encoding="utf-8"))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    install_fonts(output)
    shutil.copy2(ROOT / "cv-html.css", output / "cv-html.css")
    (output / "index.html").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
