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
    <section class="book-wrap" aria-label="{safe_title} CV">
      <div id="book" class="book"></div>
      <p id="status" class="status" role="status">Loading…</p>
      <nav class="actions" aria-label="Document controls">
        <button id="prev" type="button" aria-label="Previous page">←</button>
        <span id="page-label">Loading…</span>
        <button id="next" type="button" aria-label="Next page">→</button>
        <a href="cv.pdf" download aria-label="Download PDF" title="Download PDF">↓</a>
      </nav>
    </section>
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
      minWidth: 400,
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
    let direction = 1;
    let autoplay;
    const pause = () => {{
      clearTimeout(autoplay);
      autoplay = setTimeout(step, 5000);
    }};
    const step = () => {{
      const current = flip.getCurrentPageIndex();
      if (current >= pdf.numPages - 1) direction = -1;
      if (current <= 0) direction = 1;
      if (direction > 0) flip.flipNext("top");
      else flip.flipPrev("top");
      autoplay = setTimeout(step, 2600);
    }};
    const update = (event) => {{ label.textContent = `Page ${{event.data + 1}} / ${{pdf.numPages}}`; }};
    flip.on("flip", update);
    update({{ data: 0 }});
    document.querySelector("#prev").onclick = () => {{ flip.flipPrev("top"); pause(); }};
    document.querySelector("#next").onclick = () => {{ flip.flipNext("top"); pause(); }};
    book.addEventListener("pointerdown", pause);
    document.addEventListener("keydown", (event) => {{
      if (event.key === "ArrowLeft") {{ flip.flipPrev("top"); pause(); }}
      if (event.key === "ArrowRight") {{ flip.flipNext("top"); pause(); }}
    }});
    document.addEventListener("visibilitychange", () => {{
      clearTimeout(autoplay);
      if (!document.hidden) pause();
    }});
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) pause();
    status.remove();
  </script>
</body>
</html>'''


def viewer_css() -> str:
    return ''':root { color-scheme: dark; --ink: #fff; --bg: #171717; }
* { box-sizing: border-box; }
html, body { margin: 0; width: 100%; min-height: 100%; background: var(--bg); }
body { min-height: 100vh; overflow: hidden; font-family: system-ui, sans-serif; }
.viewer-shell { display: grid; place-items: center; width: 100vw; height: 100vh; padding: 16px; }
.book-wrap { position: relative; display: grid; place-items: center; width: min(100%, 595px); height: min(calc(100vh - 32px), 842px); }
.book { width: 100%; height: 100%; filter: drop-shadow(0 18px 34px rgb(0 0 0 / 45%)); }
.page { background: white; overflow: hidden; }
.pdf-page { display: block; width: 100%; height: 100%; object-fit: contain; }
.status { position: absolute; color: #aaa; }
.actions { position: absolute; z-index: 20; left: 50%; bottom: 18px; display: flex; align-items: center; gap: 5px; padding: 5px; border: 1px solid rgb(255 255 255 / 18%); border-radius: 999px; color: var(--ink); background: rgb(20 20 20 / 78%); box-shadow: 0 6px 24px rgb(0 0 0 / 35%); backdrop-filter: blur(10px); transform: translateX(-50%); opacity: .38; transition: opacity .2s; }
.actions:hover, .actions:focus-within { opacity: 1; }
button, .actions a { display: grid; place-items: center; width: 34px; height: 34px; padding: 0; border: 0; border-radius: 50%; color: inherit; background: transparent; font: 16px/1 system-ui, sans-serif; text-decoration: none; cursor: pointer; }
button:hover, .actions a:hover { background: rgb(255 255 255 / 14%); }
#page-label { min-width: 62px; font-size: 12px; text-align: center; white-space: nowrap; }
@media (max-width: 700px) { .viewer-shell { padding: 0; } .book-wrap { width: 100vw; height: 100vh; } .book { filter: none; } .actions { bottom: max(12px, env(safe-area-inset-bottom)); opacity: .65; } }
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

    output.mkdir(parents=True, exist_ok=True)
    for stale_pdf in output.glob("*.pdf"):
        stale_pdf.unlink()
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
