{% macro image() %}
#pad(left: {{ design.header.photo_space_left }}, right: {{ design.header.photo_space_right }}, image("{{ cv.photo.name }}", width: {{ design.header.photo_width }}))
{% endmacro %}

{% if cv.photo %}
{% set photo = "image(\"" + cv.photo|string + "\", width: "+ design.header.photo_width + ")" %}
#grid(
{% if design.header.photo_position == "left" %}
  columns: (auto, 1fr),
{% else %}
  columns: (1fr, auto),
{% endif %}
  column-gutter: 0cm,
  align: horizon + left,
{% if design.header.photo_position == "left" %}
  [{{ image() }}],
  [
{% else %}
  [
{% endif %}
{% endif %}
{% if cv.name %}
= {{ cv.name }}
{% endif %}

{% if cv.headline %}
  #headline([{{ cv.headline }}])

{% endif %}
{% if cv._connections %}
// Compact contact groups: address/phone, email/website, GitHub/LinkedIn.
#align(center)[
  #grid(
    columns: (auto, auto, auto),
    column-gutter: 0.55cm,
    row-gutter: 0.09cm,
    align: left + horizon,
    [{{ cv._connections[0] }}],
    [{{ cv._connections[1] }}],
    [{{ cv._connections[5] }}],
    [{{ cv._connections[2] }}],
    [{{ cv._connections[3] }}],
    [{{ cv._connections[4] }}],
  )
]
#v(0.31cm)
{% endif %}
{% if cv.photo %}
{% if design.header.photo_position == "left" %}
  ]
)
{% else %}
  ],
  [{{ image() }}],
)
{% endif %}
{% endif %}
