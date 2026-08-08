# SpiderVerse AI — interface specification

The accepted visual reference is `graph-explorer-concept.png` (1536 × 1024).

## Product surface

The application is a graph exploration tool, not a marketing site. The graph canvas is the dominant surface. A quiet header contains the brand, four navigation items, and global search. The desktop explorer uses three columns: filters, graph canvas, and a selected-entity inspector. A grounded question bar closes the workspace.

## Visible-copy lock for the first viewport

- `SPIDERVERSE AI`
- `Explore`, `Characters`, `Universes`, `Path Finder`
- `Search the Spider-Verse…`
- `Knowledge Graph`
- `All universes`, `All relationships`, `Reset view`
- `Explorer`, `Entity types`, `Universes`, `Relationships`
- `Selected entity`, `Powers`, `Connections`, `Appearances`, `Sources`
- `Ask anything about the Spider-Verse…`, `Ask`

Contextual entity names, relationship names, counts, source titles, validation messages, and accessibility labels are data-driven and may vary.

## Tokens

| Role | Value |
| --- | --- |
| Background | `#050b12` |
| Raised surface | `#0a121c` |
| Active surface | `#101b27` |
| Primary text | `#f5f1e8` |
| Muted text | `#9ba7b5` |
| Border | `#263341` |
| Character / active | `#f0283c` |
| Universe | `#31c6cf` |
| Event | `#f3a21b` |
| Team | `#a45ee5` |
| Work | `#84a3b8` |
| Power | `#6ecb8f` |

Spacing follows a 4 px base with primary gaps of 8, 12, 16, 24, and 32 px. Corners are 6–10 px. Borders are 1 px. Shadows are reserved for overlays; the main layout relies on borders and tonal contrast.

## Typography

- Display: `Barlow Condensed`, with `Arial Narrow` as the fallback.
- UI and content: `Inter`, with system sans-serif fallbacks.
- Titles: condensed, 600–700, tight line height.
- Controls: 13–14 px, deliberately sized; no browser-default typography.
- Metadata: 11–12 px uppercase with restrained tracking.

## Component families

- App header and navigation items with a red underline selected state.
- Search field, selects, icon buttons, primary and secondary buttons.
- Filter sections with square checkboxes and category-color markers.
- Graph nodes: circle for characters, square for universes/works, diamond for events, hexagon for teams, rounded rectangle for powers/concepts.
- Entity inspector with open sections separated by horizontal rules.
- Data rows and source rows, never nested card grids.
- Graph-grounded question bar with answer drawer.

## Responsive behavior

At widths below 1100 px, the inspector becomes a full-width panel below the canvas. Below 760 px, navigation scrolls horizontally, search moves to its own row, filters become a collapsible toolbar, and the canvas maintains a minimum height of 520 px. No primary control may overflow the viewport.

## Motion

Use 150–220 ms transitions for selection and panels. Graph motion communicates expansion or focus. Respect `prefers-reduced-motion`.

## Icon inventory

The brand uses a code-native web mark. Navigation contains no decorative icons. Search, reset, zoom, expand, relation, external-link, and send actions use consistent 1.8 px outline SVG icons through Lucide. Category symbols are geometric and code-native.

## Asset treatment

All true application UI is code-native. No character portrait or copyrighted costume art is required. Fine dotted and web-line canvas textures may be implemented in CSS because they are structural background geometry, not central raster artwork.
