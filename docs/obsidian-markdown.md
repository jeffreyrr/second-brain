# Obsidian-Flavored Markdown — conventions cheat sheet

A quick reference so wiki pages render correctly in Obsidian on **desktop and
mobile**. The assistant should follow these when writing pages; readers can skim
it to understand the syntax.

> **Attribution.** Distilled from the `obsidian-markdown` skill in
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT License).
> Rewritten and trimmed for this project; credit for the conventions is theirs.

## Links (wikilinks)

- Basic: `[[Page Name]]`
- Custom text: `[[Page Name|display text]]`
- To a heading: `[[Page Name#Heading]]`
- To a block: `[[Page Name#^block-id]]`
- Within the same page: `[[#Heading]]`

Give a paragraph a block id by appending `^block-id` on its own line or at the end.

## Embeds

Prefix any wikilink with `!` to embed it:

- Whole page: `![[Page Name]]`
- A section: `![[Page Name#Heading]]`
- Image at width: `![[diagram.png|400]]`
- PDF page: `![[paper.pdf#page=3]]`

## Callouts

```
> [!note] Optional title
> body text

> [!warning]- Collapsed by default
> hidden until expanded
```

Useful types: `note`, `info`, `tip`, `warning`, `danger`, `example`, `todo`,
`success`, `question`, `quote`. Suffix `-` = start collapsed, `+` = start expanded.

## Properties (frontmatter)

YAML block at the very top of the file — Obsidian reads it as Properties:

```yaml
---
title: Human Readable Title
type: source
created: 2026-08-03
updated: 2026-08-03
sources: [some-source-slug]
tags: [topic, subtopic]
aliases: [Other Name People Use]
---
```

`tags` and `aliases` are optional but make pages easier to find in Obsidian.

## Tags

Inline `#tag` or nested `#area/topic`. Letters, numbers (not first char),
`_`, `-`, `/`. Prefer a handful of consistent tags over many one-off ones.

## Other syntax that renders in Obsidian

- Highlight: `==text==`
- Hidden comment (not rendered): `%%note to self%%`
- Math (LaTeX): `$inline$`, `$$block$$`
- Diagrams: ```` ```mermaid ```` code blocks
- Footnotes: `claim[^1]` … `[^1]: source`

## Keep it portable

These all degrade gracefully — a plain markdown viewer that doesn't know Obsidian
still shows readable text. Don't rely on any Obsidian *plugin* syntax; stick to
the core features above so the wiki stays useful in any editor and on any OS.
