# Second Brain

**Repo:** [github.com/jeffreyrr/second-brain](https://github.com/jeffreyrr/second-brain)

A portable, self-contained knowledge base your AI assistant maintains for you. Drop in
sources — articles, notes, even past chats — and Claude reads them and keeps a
cross-linked Markdown wiki you fully own: searchable, syncable, and readable in any
editor. **You read it; Claude writes it.** No app, no database, no lock-in — just
Markdown plus a couple of optional Python helpers. Extract the folder anywhere (macOS
or Windows) and point your assistant at `CLAUDE.md`.

## Features

- **Capture & ingest** ([how](#use-it)) — drop files, URLs, or notes; Claude summarizes and cross-links them into pages.
- **Ask & digest** ([how](#use-it)) — cited answers to your questions, plus "what's new" recaps.
- **Health-check** ([how](#use-it)) — finds contradictions, orphans, and gaps; nudges ~weekly.
- **Import past chats** ([details](docs/guide.md#import-past-chats)) — pull durable topics from ChatGPT / Claude / Gemini / Perplexity exports, selectively.
- **Local search** ([details](docs/guide.md#running-the-python-helpers)) — fast BM25 over the whole wiki.
- **Sync & mobile** ([details](docs/guide.md#sync-and-mobile)) — read and capture from any device.
- **Obsidian view** ([details](docs/guide.md#using-obsidian)) — browse the linked graph on desktop or phone.
- **Backups & restore** ([details](docs/guide.md#backups-and-restore)) — timestamped snapshots plus per-file version history.
- **Optional add-ons** ([details](docs/guide.md#optional-add-ons)) — defuddle web clipper, Obsidian Canvas/Bases, qmd search upgrade.

```
raw/       your sources (you add; Claude never edits)
wiki/      the wiki Claude maintains (summaries, entities, concepts, index, log)
tools/     search.py, chat_import.py, backup.py — local helpers (need Python; Claude Code)
docs/      guide.md + Obsidian-markdown conventions
CLAUDE.md  the rulebook Claude follows
```

## Setup

Add **one line** to your assistant's **system prompt** (custom instructions), with
the absolute path to `CLAUDE.md`:

```
At the start of every session, read and follow <ABSOLUTE-PATH>/CLAUDE.md — it configures you as the maintainer of my second-brain wiki.
```

Get the path (no terminal needed):
- **macOS:** right-click `CLAUDE.md` → hold **Option (⌥)** → **Copy … as Pathname**
- **Windows:** **Shift + right-click** `CLAUDE.md` → **Copy as path** (drop the `"quotes"`)

Needs an assistant with file access to this folder — Claude Desktop or claude.ai with
a filesystem connector, or Claude Code. The core wiki needs only file read/write; the
Python helpers (`search.py`, `chat_import.py`) and shell-based add-ons (defuddle, qmd)
run only in **Claude Code** or another env that can execute code. See
[`docs/guide.md`](docs/guide.md) to check or set up Python.

> **Start a new chat after saving the system prompt.** It only takes effect in
> chats opened afterward — your current session won't pick it up.

## Use it

New here? Just say **`getting started`** and Claude walks you through your first source.

- **Add:** drop a file into `raw/`, say `ingest <filename>` (or `ingest all`).
- **Capture:** say `remember this: …` — Claude files a quick note for you, no fuss.
- **Ask:** `what does the wiki say about X?` — Claude answers with citations.
- **Catch up:** `what's new?` — a short digest of what you've added lately.
- **Maintain:** `health-check the wiki`. Claude also nudges ~weekly, only when needed.
- **Back up:** `back up my brain` — a timestamped snapshot (Claude Code). Your sync
  service also keeps per-file history; see [Backups and restore](docs/guide.md#backups-and-restore).
- **Import past chats:** say `ingest my chat history` — Claude groups your ChatGPT /
  Claude / Gemini exports by topic and asks which to keep. See [Import past chats](docs/guide.md#import-past-chats).

> **Tip:** ingest and health-check in a **clean chat session**. A fresh session keeps
> Claude focused on the wiki and avoids dragging in unrelated context from a long chat.

---

Every feature in depth → [`docs/guide.md`](docs/guide.md) · the assistant's full rulebook → `CLAUDE.md`.

## License

MIT — see [`LICENSE`](LICENSE). Reuses MIT-licensed conventions from
[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills); attributions are in
[`docs/guide.md`](docs/guide.md#optional-add-ons).
