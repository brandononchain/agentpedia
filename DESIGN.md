---
name: Agentpedia
description: The open encyclopedia of agents and skills.
colors:
  verdigris: "#0e4f57"
  verdigris-dark: "#9fd4ce"
  selection: "#c5ddd8"
  selection-ink: "#102326"
  selection-dark: "#1d4a47"
  paper: "#f4efe4"
  paper-dark: "#16130f"
  ink: "#1c1915"
  ink-dark: "#f3eee4"
  muted-ink: "#534e45"
  muted-ink-dark: "#d4cbbd"
  rule: "rgba(28, 25, 21, 0.22)"
  rule-dark: "rgba(243, 238, 228, 0.22)"
  code-paper: "#e9e2d4"
  code-paper-dark: "#241f1a"
  clean: "#1d5c38"
  clean-dark: "#b7e0c6"
  noted: "#6b4a12"
  noted-dark: "#e6c48a"
  blocked: "#8d1d1d"
  blocked-dark: "#f0b4b0"
typography:
  display:
    fontFamily: "Literata, Georgia, 'Iowan Old Style', serif"
    fontSize: "clamp(3.1rem, 8vw, 5.4rem)"
    fontWeight: 600
    lineHeight: 0.92
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Literata, Georgia, 'Iowan Old Style', serif"
    fontSize: "clamp(2.15rem, 4vw, 3.15rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Literata, Georgia, 'Iowan Old Style', serif"
    fontSize: "1.55rem"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.03em"
  body:
    fontFamily: "Literata, Georgia, 'Iowan Old Style', serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "normal"
  label:
    fontFamily: "'Atkinson Hyperlegible', 'Segoe UI', sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
  mono:
    fontFamily: "'Geist Mono', ui-monospace, monospace"
    fontSize: "0.78rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
rounded:
  none: "0"
spacing:
  "0.35": "0.35rem"
  "0.45": "0.45rem"
  "0.75": "0.75rem"
  "1": "1rem"
  "1.6": "1.6rem"
  "2": "2rem"
components:
  button-solid:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.none}"
    padding: "0.3rem 0.7rem"
  button-solid-hover:
    backgroundColor: "{colors.verdigris}"
    textColor: "{colors.paper}"
    rounded: "{rounded.none}"
    padding: "0.3rem 0.7rem"
  button-portal:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.none}"
    padding: "0 1.25rem"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.verdigris}"
    rounded: "{rounded.none}"
    padding: "0"
  button-text-current:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0"
  field:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.45rem 0"
  field-portal:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.65rem 0.6rem 0.65rem 0"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0"
  nav-link-current:
    backgroundColor: "transparent"
    textColor: "{colors.verdigris}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0"
  plate:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.75rem 0 1rem"
  shelf-cell:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.9rem 1rem 0.85rem"
  snippet:
    backgroundColor: "{colors.code-paper}"
    textColor: "{colors.ink}"
    typography: "{typography.mono}"
    rounded: "{rounded.none}"
    padding: "0.85rem 1rem"
  entry-title:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.headline}"
    rounded: "{rounded.none}"
    padding: "0 0 0.35rem 0"
  score-clean:
    textColor: "{colors.clean}"
  score-noted:
    textColor: "{colors.noted}"
  score-blocked:
    textColor: "{colors.blocked}"
---

# Design System: Agentpedia

## Overview

**Creative North Star: "The Reference Desk"**

Agentpedia is a reference desk on warm paper. The portal answers what the encyclopedia holds: a serif name, a tagline, one verdigris rule, a search, a counts line, and shelves of names. An entry is an article, with a title, a lede, a reading column, and a ruled plate of facts. The tone is scholarly and plain.

Literata carries titles and the reading column. Atkinson Hyperlegible carries chrome. Geist Mono carries code and counts. Corners are square. Depth comes from a hairline, a double ink rule, or a code-paper block, never from a shadow. A CSS turbulence overlay grains the paper. Dark mode keeps the same roles on dark paper.

The desk does not borrow another reference work’s logo, wordmark, or skin. Streetwear, daylight, data-strobe, cutting-bench, orienteering, and monochrome marketing are declined: they drop the pinned paper and ink, or they stop the page reading as an article.

**Key Characteristics:**

- Warm paper, near-black ink, and one verdigris accent
- Literata for reading and titles; Atkinson Hyperlegible for chrome; Geist Mono for code and counts
- Square corners, with rules instead of shadows
- A double ink rule on titles and plates, and one verdigris rule under the portal tagline
- Paper grain as a CSS turbulence overlay, with no shipping rasters
- Dark paper repeats the same relationship

## Colors

The palette is warm paper and near-black ink, with one deep verdigris accent. Dark mode reassigns those roles. It is the same desk with the lights down.

### Primary

- **Verdigris** (#0e4f57): the only accent on light paper. Links, the focus outline, the caret, the portal rule, and the solid-button hover.
- **Pale verdigris** (#9fd4ce): the same accent on dark paper.
- **Selection wash** (#c5ddd8): the light-paper text selection, with **Selection ink** (#102326). That ink is also the solid-button label when the button hovers on dark paper.
- **Selection on dark paper** (#1d4a47): the dark-paper selection wash. Selection text on dark paper uses the dark ink.

### Neutral

- **Warm paper** (#f4efe4): the page, cards, and popover surface on the light desk. **Dark paper** (#16130f) replaces it under `.dark`.
- **Near-black ink** (#1c1915): text, the solid button, underlines, and the double rule. **Dark ink** (#f3eee4) replaces it on dark paper.
- **Muted ink** (#534e45): secondary prose, placeholders, counts, plate labels, the quiet date, and the scrollbar thumb. **Muted ink on dark paper** (#d4cbbd) replaces it.
- **Hairline** (rgba(28, 25, 21, 0.22)): borders on the header, shelves, tables, prose headings, and code blocks. **Hairline on dark paper** (rgba(243, 238, 228, 0.22)) replaces it.
- **Code paper** (#e9e2d4): the block behind snippets and preformatted code. **Code paper on dark** (#241f1a) replaces it.
- **Clean** (#1d5c38), **Noted** (#6b4a12), and **Blocked** (#8d1d1d): lint ink for the score mark and the changelog “added” mark. On dark paper they become **Clean on dark** (#b7e0c6), **Noted on dark** (#e6c48a), and **Blocked on dark** (#f0b4b0).

### Named Rules

**The One Accent Rule.** Verdigris is the only accent. It marks links, focus, the portal rule, and the solid-button hover. Clean, noted, and blocked are lint ink, not a second brand color.

**The Same Relationship Rule.** Dark mode reassigns paper, ink, accent, rule, code paper, and the three lint inks. It does not introduce a new brand.

## Typography

**Display Font:** Literata (Georgia, Iowan Old Style, serif)

**Body Font:** Literata for the reading column; Atkinson Hyperlegible (Segoe UI, sans-serif) for chrome

**Label/Mono Font:** Atkinson Hyperlegible for labels; Geist Mono (ui-monospace, monospace) for code and counts

**Character:** A text face for reading, a highly legible sans for wayfinding, and a mono for anything a reader might copy or count. Titles are semibold and slightly tight. Chrome is regular, with no uppercase tracking.

### Hierarchy

- **Display** (600, clamp(3.1rem, 8vw, 5.4rem), line-height 0.92, letter-spacing -0.035em): the centered portal name. The running header wordmark is the same face at 1.45rem, line-height 1, letter-spacing -0.03em. The footer name is 1.4rem.
- **Headline** (600, clamp(2.15rem, 4vw, 3.15rem), line-height 1.08, letter-spacing -0.03em): the entry title. A double ink rule sits under it.
- **Title** (600, 1.55rem, line-height 1.08, letter-spacing -0.03em): module headings on the portal. Article section titles (“See also”, “References”) use the same weight, leading, and tracking at 1.45rem. Prose h2 is 1.55rem with line-height 1.2, letter-spacing -0.02em, and a hairline underneath. A date inside a module heading drops to weight 400. Shelf names are 1.35rem at letter-spacing -0.02em. Plate names are 1.25rem.
- **Body** (400, 1.0625rem, line-height 1.65): the reading column, max 70ch. The lede under a title is Literata at 1.2rem and line-height 1.45, also max 70ch. Prose headings stay in Literata; tables inside prose switch back to Atkinson Hyperlegible at 0.92rem.
- **Label** (400, 0.95rem, line-height 1.55): navigation, footer lists, and header search. Quiet labels (crumbs, plate terms, the score word) are 0.92rem in muted ink.
- **Mono** (400, 0.78rem in blocks, line-height 1.55): snippets and preformatted code. Inline code is 0.86em. The score numeral is 1rem. Shelf counts and letter jumps use tabular figures.

### Named Rules

**The Two Jobs Rule.** Literata carries the portal name, entry titles, section headings, shelf names, plate names, the lede, and the reading column. Atkinson Hyperlegible carries navigation, search, buttons, labels, tables, and the footer. Geist Mono carries code and measured counts.

**The Article Measure Rule.** The lede, the reading column, see-also, references, glossary definitions, and empty notes stay within 70ch.

## Layout

The page is one centered frame: `min(76rem, calc(100% - 2rem))`. The portal, the header, the footer, the article, and the browse page all use it. The frame’s side inset is the 2rem spacing step. Inside it, the rhythm is the recorded steps: 0.35rem for inline gaps (crumbs, tags, plate rows), 0.45rem for tight stacks, 0.75rem under a double rule and inside the contents box, 1rem for cell and snippet padding, 1.6rem between the reading column and the plate, and 2rem before see-also and at the page edge.

The portal stacks the name, the tagline, the verdigris rule, the search, the counts, a shelf grid, then three reading modules. Shelves are two columns, three from 800px. Below 800px, a trailing odd shelf spans the row. Modules stack until 960px, then sit in `1.25fr 1fr 1fr`.

An article is a rail plus a column. From 1100px the rail is 13.25rem and sticky (top 4.25rem), and the body splits into a reading column capped at 70ch and a plate of `minmax(16rem, 19.5rem)`. Below that, the rail is a horizontal scroller with a hairline under it. Browse uses the same idea from 960px: a 14rem filter column beside the results.

The header is sticky, with a hairline along its bottom. From 860px it becomes a grid: wordmark, theme toggle, wrapping navigation, then a full-width search. The portal search stacks under 560px; the field keeps its ink underline and the button sits at the end. The footer is a single column until 720px, then three, and it opens with a double rule after 4.5rem of air.

### Named Rules

**The Ruled Column Rule.** Every page frame is min(76rem, calc(100% - 2rem)), centered. At 1100px an article places a 13.25rem rail beside a reading column no wider than 70ch, with the plate in a 16–19.5rem track.

## Elevation & Depth

The system is flat. The shipping stylesheet sets no drop shadow. Separation is tonal and linear: the page is paper, code sits on a deeper code paper, and a hovered shelf picks up an 8% verdigris wash (`color-mix(in srgb, var(--accent-ink) 8%, transparent)`). A double rule or a hairline does the rest.

Grain is a fixed overlay on the body, painted with an inline SVG turbulence filter (fractalNoise, baseFrequency 0.8, two octaves, stitchTiles, tiled at 180px). It does not receive pointer events. On light paper it is opacity 0.045 with multiply. On dark paper it is opacity 0.07 with overlay. The overlay is z-index 80, the sticky header is 40, and the skip link is 90, so the grain covers the page and the skip link still clears it.

### Named Rules

**The Flat Paper Rule.** Surfaces are flat. Depth is a hairline, a double rule, a code-paper block, or an 8% verdigris wash on a shelf. There is no drop shadow.

**The Grain Rule.** Texture is the fixed turbulence overlay on the body: opacity 0.045 and multiply on light paper, opacity 0.07 and overlay on dark paper. It is not an image asset.

## Shapes

Corners are square. The radius scale is a single step, 0, and the theme radii are all that step, so controls, plates, shelves, and code blocks do not curve.

The line is the form. A 1px hairline divides the header, the shelf grid, prose h2s, tables, see-also, and code blocks. A 3px double ink rule opens an entry title (the rule is drawn under the words), a portal module, an empty note, the footer, and an infobox plate (the plate closes with a hairline). The portal rule is the one exception: a 1px verdigris line, `min(14rem, 40%)` wide, centered under the tagline.

### Named Rules

**The Square Rule.** Radius is 0 on every corner, including controls, plates, and code blocks.

**The Double Rule.** A 3px double ink rule opens an entry title (drawn under the title), a module, an empty note, the footer, and an infobox plate. The single verdigris rule is only the portal rule under the tagline.

## Components

Controls are ink on paper, or verdigris type with no fill. The current item in a set is marked by swapping the underline, not by a chip or a pill.

### Buttons

- **Shape:** square (0).
- **Primary:** an ink rectangle with paper text. Header search, the shared solid button, and error retry use 0.3rem 0.7rem. The portal submit uses 0 1.25rem at 1.05rem type, and it stretches to the field.
- **Hover / Focus:** the fill becomes verdigris and the label stays paper. On dark paper the hover label is selection ink. Focus is a 2px verdigris outline, offset 3px, on links, buttons, fields, selects, and summaries.
- **Text:** transparent, verdigris, underlined, offset 0.18em, with no padding. This is the theme toggle, the copy control, the rail’s “Random entry”, and the install targets. Pressed or selected, the label turns ink, the underline comes off, and a 1px ink rule sits under the word.

### Cards / Containers

- **Infobox plate:** square, paper, a double ink rule on top, a hairline on the bottom, padding 0.75rem 0 1rem. The name is Literata at 1.25rem. Facts are a two-column list, 6.2rem for the term. Terms are muted ink at 0.92rem. Links inside are verdigris. A missing version reads “Not recorded”.
- **Shelf cell:** a hairline grid. Each cell is at least 5.6rem tall, padded 0.9rem 1rem 0.85rem, with the serif name at the start and a tabular count in muted ink at the end. Hover washes the cell with 8% verdigris and turns the name verdigris.
- **Contents:** a hairline box, max 24rem, padded 0.75rem 0.95rem 0.85rem, with a Literata heading at 1.2rem. Nested items use lower-alpha markers.
- **Snippet:** code paper, a hairline, padding 0.85rem 1rem, Geist Mono at 0.78rem and line-height 1.55. Inline path code can drop the box and keep the face.
- **Shadow Strategy:** none. See Elevation & Depth.

### Inputs / Fields

- **Style:** transparent, square, ink text, muted placeholder, verdigris caret. Browse fields and the header search use a 1px ink underline. The portal search uses a 2px ink underline and 1.25rem type, padded 0.65rem 0.6rem 0.65rem 0.
- **Focus:** the 2px verdigris outline, offset 3px. The underline does not change color.
- **Portal search under 560px:** the form stacks, the field keeps the 2px underline, and the button aligns to the end.

### Navigation

The header wordmark is the serif name. Links are Atkinson Hyperlegible at 0.95rem, ink, with no underline until hover or the current page, when they turn verdigris and underline. The article rail uses verdigris links; the current shelf is ink with a 1px ink rule and no underline. Crumbs match that: verdigris links, a slash separator, and the current crumb in ink with no underline. The theme control is a text button labeled for the paper it will switch to.

### Portal rule

A 1px verdigris line under the tagline. It draws once, from the left, over 900ms with `cubic-bezier(0.16, 1, 0.3, 1)`. When the reader prefers reduced motion, the rule is already drawn. This is the only signature motion.

### Score mark

An inline pair: a tabular mono numeral at 1rem, then the word at 0.92rem. Clean, noted, and blocked use the three lint inks. The mark sits in the plate and in results. It is a fact line, not a badge.

### Named Rules

**The Underline Control Rule.** Search and fields are transparent, with an ink underline (1px in the header and on browse fields, 2px on the portal search). A solid action is an ink rectangle that turns verdigris on hover. A text action is a verdigris underline with no fill; the current or pressed text action switches to ink with a 1px ink rule.

## Do's and Don'ts

### Do:

- **Do** keep light paper, ink, and verdigris on #f4efe4, #1c1915, and #0e4f57, and dark paper, ink, and verdigris on #16130f, #f3eee4, and #9fd4ce.
- **Do** focus with a 2px verdigris outline offset 3px, and keep the skip link in ink on paper.
- **Do** draw the portal rule over 900ms with cubic-bezier(0.16, 1, 0.3, 1), and leave it fully drawn when the reader asks for reduced motion.
- **Do** set shelf counts and lint scores in Geist Mono with tabular figures.
- **Do** take the display name from SITE_NAME.

### Don't:

- **Don't** add a second accent, a gradient, or a drop shadow.
- **Don't** round corners.
- **Don't** ship a raster texture, logo, or wordmark. Grain stays the CSS turbulence overlay.
- **Don't** set the reading column in Atkinson Hyperlegible.
- **Don't** set navigation, buttons, or meta labels in Literata.
- **Don't** print a version, a price, or a customer mark. An unrecorded version stays “Not recorded”.
