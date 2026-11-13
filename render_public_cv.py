#!/usr/bin/env python3
"""Build public CV PDF and a book-style PDF.js viewer."""
from __future__ import annotations

import argparse
import html
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent


def viewer_html(title: str) -> str:
    safe_title = html.escape(title)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{safe_title} — curriculum vitae">
  <title>{safe_title} — CV</title>
  <link rel="stylesheet" href="viewer.css">
</head>
<body>
  <main class="viewer-shell">
    <header class="viewer-header">
      <div>
        <p class="eyebrow">Curriculum vitae</p>
        <h1>{safe_title}</h1>
      </div>
      <nav class="actions" aria-label="Document actions">
        <button id="prev" type="button" aria-label="Previous page">←</button>
        <span id="page-label">Loading…</span>
        <button id="next" type="button" aria-label="Next page">→</button>
        <a href="cv.pdf" download>Download PDF</a>
      </nav>
    </header>

    <section class="book-wrap" aria-label="CV book">
      <div id="book" class="book"></div>
      <p id="status" class="status" role="status">Loading document…</p>
    </section>
    <p class="hint">Drag page corner, use arrow keys, or tap page edges.</p>
  </main>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.mjs" type="module"></script>
  <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
  <script type="module">
    const pdfjs = await import("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.mjs");
    pdfjs.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.mjs";
    const pdf = await pdfjs.getDocument("cv.pdf").promise;
    const book = document.querySelector("#book");
    const status = document.querySelector("#status");
    const label = document.querySelector("#page-label");
    const pages = [];
    const scale = 1.5;

    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {{
      const pdfPage = await pdf.getPage(pageNumber);
      const viewport = pdfPage.getViewport({{ scale }});
      const canvas = document.createElement("canvas");
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      canvas.className = "pdf-page";
      canvas.setAttribute("aria-label", `Page ${{pageNumber}} of ${{pdf.numPages}}`);
      await pdfPage.render({{ canvasContext: canvas.getContext("2d"), viewport }}).promise;
      const page = document.createElement("div");
      page.className = "page";
      page.append(canvas);
      book.append(page);
      pages.push(page);
    }}

    const flip = new St.PageFlip(book, {{
      width: 595,
      height: 842,
      size: "stretch",
      minWidth: 280,
      maxWidth: 595,
      minHeight: 396,
      maxHeight: 842,
      maxShadowOpacity: 0.28,
      showCover: true,
      mobileScrollSupport: true,
      usePortrait: true,
      flippingTime: 700,
    }});
    flip.loadFromHTML(pages);
    const update = (event) => {{ label.textContent = `Page ${{event.data + 1}} / ${{pdf.numPages}}`; }};
    flip.on("flip", update);
    update({{ data: 0 }});
    document.querySelector("#prev").onclick = () => flip.flipPrev();
    document.querySelector("#next").onclick = () => flip.flipNext();
    document.addEventListener("keydown", (event) => {{
      if (event.key === "ArrowLeft") flip.flipPrev();
      if (event.key === "ArrowRight") flip.flipNext();
    }});
    status.remove();
  </script>
</body>
</html>'''


def viewer_css() -> str:
    return '''@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@500;600&display=swap");
:root { color-scheme: dark; --ink: #f5f1ea; --muted: #b5aea3; --accent: #EE2D2E; --bg: #171717; --panel: #22201e; }
* { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; color: var(--ink); background: radial-gradient(circle at 50% -20%, #4a302d, var(--bg) 45%); font-family: "DM Sans", sans-serif; }
.viewer-shell { width: min(1180px, 100%); margin: auto; padding: 34px 24px 28px; }
.viewer-header { display: flex; align-items: end; justify-content: space-between; gap: 24px; margin-bottom: 26px; }
.eyebrow { margin: 0 0 5px; color: var(--accent); font-size: 11px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }
h1 { margin: 0; font-family: "Playfair Display", Georgia, serif; font-size: clamp(25px, 4vw, 42px); font-weight: 500; }
.actions { display: flex; align-items: center; gap: 9px; color: var(--muted); font-size: 13px; white-space: nowrap; }
button, .actions a { border: 1px solid #514b45; border-radius: 5px; padding: 8px 12px; color: var(--ink); background: #292623; font: inherit; text-decoration: none; cursor: pointer; }
button:hover, .actions a:hover { border-color: var(--accent); }
#page-label { min-width: 75px; text-align: center; }
.book-wrap { position: relative; display: grid; place-items: center; min-height: min(78vh, 840px); padding: 20px; border: 1px solid #3a3530; border-radius: 12px; background: linear-gradient(135deg, #302a27, #191817); box-shadow: 0 25px 80px rgb(0 0 0 / 35%); }
.book { width: min(78vw, 595px); height: min(78vh, 842px); }
.page { background: white; overflow: hidden; }
.pdf-page { display: block; width: 100%; height: 100%; object-fit: contain; }
.status { position: absolute; color: var(--muted); }
.hint { margin: 15px 0 0; color: var(--muted); font-size: 12px; text-align: center; }
@media (max-width: 700px) { .viewer-shell { padding: 20px 12px; } .viewer-header { display: block; } .actions { margin-top: 16px; } .book-wrap { min-height: 0; padding: 10px; } .book { width: min(92vw, 595px); height: min(78vh, 842px); } }
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "cv.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "rendered" / "public")
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    cv = data["cv"]

    # Public page keeps email as its only contact method.
    for field in ("location", "phone", "website", "social_networks", "custom_connections"):
        cv.pop(field, None)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", dir=source.parent, encoding="utf-8", delete=False) as public_source:
        yaml.safe_dump(data, public_source, allow_unicode=True, sort_keys=False)
        public_source_path = Path(public_source.name)
    try:
        subprocess.run([
            "rendercv", "render", str(public_source_path), "--output-folder", str(output),
            "--dont-generate-html", "--dont-generate-markdown", "--dont-generate-png",
        ], cwd=ROOT, check=True)
    finally:
        public_source_path.unlink(missing_ok=True)

    generated_pdf = next(output.glob("*.pdf"))
    generated_pdf.rename(output / "cv.pdf")
    for path in output.glob("*.typ"):
        path.unlink()
    (output / "viewer.css").write_text(viewer_css(), encoding="utf-8")
    (output / "index.html").write_text(viewer_html(cv["name"]), encoding="utf-8")


if __name__ == "__main__":
    main()
