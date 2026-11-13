# CV and Cover Letter Rendering

Public portfolio repository for Julià Delos Ayllón. Application documents for Blender. Source files stay at repository root. Generated files belong under `generated/`.

## License

- Personal CV, cover letters, and other personal content: **CC BY-NC-SA 4.0**. See [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md).
- Rendering code and templates: **GPL-3.0-or-later**. See [`LICENSE`](LICENSE).

Attribution does not grant permission to impersonate Julià Delos Ayllón, reuse personal data as your own identity, or suggest endorsement or affiliation.

## Tools

### CV

- **RenderCV v2.8**: reads `cv.yaml` and generates CV outputs.
- **Typst**: RenderCV uses Typst for PDF typesetting.
- **YAML**: CV content, design, locale, and rendering settings live in `cv.yaml`.
- **RenderCV schema**: `cv.yaml` references the v2.8 schema for editor validation.

### Cover letter

- **Markdown**: letter content lives in `cover_letter.md`.
- **Python 3**: `render_cover_letter.py` reads front matter and converts Markdown.
- **Pandoc**: converts Markdown body to Typst markup.
- **Typst Python binding**: compiles the generated Typst source into PDF.
- **Typst template**: `cover_letter.typ` controls layout and styling.

Check installed versions:

```bash
rendercv --version
pandoc --version
python --version
```

Expected currently: RenderCV 2.8, Pandoc 3.11, Python 3.14.7.

## Source files

| File | Purpose |
|---|---|
| `cv.yaml` | CV content and RenderCV configuration |
| `cover_letter.md` | Cover-letter content and metadata front matter |
| `cover_letter.typ` | Cover-letter Typst layout |
| `render_cover_letter.py` | Markdown-to-Typst-to-PDF rendering script |
| `AGENTS.md` | Project rules for protected sources and generated output |

`cv.yaml`, `cover_letter.md`, and `cover_letter.typ` are manually maintained source files. Do not modify them automatically. Ask user before changing source content or templates.

## Render CV

Render all standard outputs into `generated/`:

```bash
rendercv render cv.yaml --output-folder generated
```

RenderCV generates PDF, PNG, HTML, Markdown, and Typst output unless disabled. Rendered files use the CV name as filename.

Useful preview command:

```bash
rendercv render cv.yaml \
  --output-folder generated \
  --dont-generate-pdf \
  --dont-generate-html \
  --dont-generate-markdown
```

This keeps PNG output for quick page and layout checks.

## Render cover letter

```bash
python render_cover_letter.py --output generated/cover_letter.pdf
```

The script:

1. Reads front matter and body from `cover_letter.md`.
2. Converts Markdown body to Typst with Pandoc.
3. Injects metadata into `cover_letter.typ` placeholders.
4. Writes generated Typst beside the PDF as `generated/cover_letter.typ`.
5. Compiles PDF with the Typst Python binding.

Custom source or output paths:

```bash
python render_cover_letter.py \
  path/to/letter.md \
  --template path/to/template.typ \
  --output generated/cover_letter.pdf
```

## CV customizations already applied

### Theme and page

- RenderCV theme: `sb2nov`.
- Paper: A4.
- Margins: top `1.1cm`, bottom `1.0cm`, left `1.3cm`, right `1.3cm`.
- Footer disabled.
- Top note disabled.
- Page-breaks inside entries disabled.

### Brand styling

Shared accent color: `#EE2D2E`.

Applied to:

- CV headline.
- Section titles.
- Links.
- Highlighted metrics and important values through inline Typst commands.

### Typography and spacing

- Body size: `10pt`.
- Name size: `25pt`.
- Headline size: `12pt`.
- Contact size: `9pt`.
- Section-title size: `12.5pt`.
- Line spacing: `0.45em`.
- Reduced spacing above and below section titles.
- Tightened spacing between regular entries, text entries, and highlight bullets.
- Date/location column width: `5.3cm`.

### Header and contact links

- LinkedIn and GitHub connections enabled.
- Contact icons shown.
- Usernames displayed instead of full URLs.
- Links remain clickable.
- Custom company links added for La Calçotada:
  - Website.
  - Instagram.
- Headline includes a Typst line break and birth/location line.

### Content structure

CV currently contains:

- Profile.
- Experience.
- Education.
- Independent Projects.
- Skills.
- Certifications and Grants.
- Patent portfolio.

Experience and project entries use RenderCV dates, locations, summaries, and highlights. Selected metrics use inline Typst styling, for example `#text(accent, weight: "bold")[10,000 users]`.

## Cover-letter customizations already applied

### Page and typography

- A4 page.
- Margins: top `1.55cm`, bottom `1.5cm`, left/right `1.35cm`.
- No header or footer.
- Font: `New Computer Modern`.
- Body size: `10pt`.
- Justified paragraphs.
- Custom paragraph leading and spacing.

### Visual design

- Shared accent color: `#EE2D2E`.
- Two-column layout.
- Sidebar width: `4.25cm`.
- Sidebar contains:
  - Initial-based large name treatment.
  - Uppercase role in accent color.
  - Sender name and address.
  - Phone and email in accent color.
- Main column contains:
  - Top rule.
  - Date.
  - Recipient details.
  - Salutation.
  - Markdown-converted letter body.
- Links use accent color.
- Sidebar disables hyphenation.

### Metadata placeholders

`render_cover_letter.py` injects these values from `cover_letter.md` front matter:

- Sender name, role, address, town, country, phone, email.
- Date.
- Recipient name, company, address, and salutation.
- Birth date and place fields are available in metadata for future template use.

## Output policy

Do not edit generated files manually. Re-render from source after every source or template change.

Use `generated/` for new output:

```text
generated/
├── cover_letter.pdf
├── cover_letter.typ
├── CV.pdf
├── CV.png
├── CV.html
└── CV.md
```

Older local outputs may exist under `rendered/`; treat them as historical output. New renders should use `generated/`.

## Validation checklist

1. Run CV render.
2. Run cover-letter render.
3. Inspect generated PDF page count and PNG previews.
4. Check links, dates, contact details, margins, and page breaks.
5. Check generated Typst source when layout differs from expectation.
6. Keep source changes in root files and generated artifacts under `generated/`.
