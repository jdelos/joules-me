// Cover-letter layout. Edit colors, sizes, spacing, and sidebar here.
// render_cover_letter.py injects metadata and Markdown-converted body at markers.

#set page(
  paper: "a4",
  margin: (top: 1.55cm, bottom: 1.5cm, left: 1.35cm, right: 1.35cm),
  header: none,
  footer: none,
)

#set text(
  font: "New Computer Modern",
  size: 10pt,
  fill: black,
)
#set par(
  justify: true,
  leading: 0.45em,
  spacing: 1.2em,
)
#let accent = rgb("EE2D2E")
#show link: set text(fill: accent)
#let sidebar-width = 4.25cm

#let sidebar = [
  #set par(justify: false, leading: 0.65em)
  #set text(hyphenate: false)
  #text(
    size: 22pt,
    weight: "bold",
    tracking: -0.02em,
  )[#text(size: 26pt)[{{name_initial}}]{{name_rest}}]
  #v(0.20cm)
  #block(width: 100%)[
    #text(
      size: 11pt,
      weight: "bold",
      fill: accent,
    )[{{role_upper}}]
  ]
  #v(0.08cm)
  #line(length: 0.5cm, stroke: 0.8pt + black)
  #v(0.32cm)
  #strong[{{name}}]
  #linebreak()
  {{address}}
  #linebreak()
  {{town}}
  #linebreak()
  {{country}}
  #v(0.25cm)
  #text(size: 8.5pt, fill: accent)[{{phone}}]
  #linebreak()
  #text(size: 8.5pt, fill: accent)[{{email}}]
]

#grid(
  columns: (sidebar-width, 1fr),
  gutter: 0.45cm,
  [
    #sidebar
  ],
  [
    #line(length: 100%, stroke: 1.2pt + black)
    #v(0.45cm)
    #text(fill: rgb("555555"), size: 9pt, weight: "bold")[{{date}}]
    #v(0.95cm)
    #strong[{{recipient_name}}]
    #linebreak()
    {{recipient_company}}
    #linebreak()
    {{recipient_address}}
    #v(0.52cm)
    {{salutation}}
    #v(0.18cm)
    {{body}}
  ],
)
