# Extra notes

Optional detail for the second brain. The `README.md` covers setup and daily use;
this is everything else. Nothing here is required to get started.

## Sync and mobile

Plain files sync through any service — Google Drive, Dropbox, or Obsidian Sync
(Google Drive and Dropbox both travel across iPhone **and** Android).

- **Read on your phone — yes.** Any markdown app; Obsidian is the natural fit
  (`[[wikilinks]]` and graph view work on mobile).
- **Capture on your phone — yes.** Save a file into `raw/`, ingest it later.
- **Maintain from your phone — no.** The ingest / query / lint loop needs a desktop
  or laptop. Model: **capture and read anywhere, let Claude write at a computer.**

Two gotchas:
- **Keep the folder available offline** — services like Google Drive File Stream
  leave online-only placeholders; set *Available offline* / *Keep on this device* so
  Claude reads real files, not stubs.
- **One writer at a time** — an ingest edits 10+ files; don't run Claude against the
  same synced folder on two machines at once, or you'll get conflict copies.

## Backups and restore

Two layers of safety — you rarely have to think about either.

**Restore a single file (automatic, no setup).** Your sync service keeps version
history, so a bad edit rolls back easily:
- **Google Drive:** on [drive.google.com](https://drive.google.com), right-click the
  file → **Manage versions** (or **File → Version history** in a Google editor).
  Deleted a whole file? Restore it from **Trash**.
- **Dropbox:** on [dropbox.com](https://dropbox.com), right-click the file → **Version
  history** → pick a version → **Restore**. Deleted files come back from **Deleted files**.

**Full snapshot (before a big change).** Grab a complete point-in-time copy.

**Prompt:**

> Back up my brain.

In Claude Code this runs `python3 tools/backup.py`, writing a timestamped
`…-backup-YYYY-MM-DD.zip` next to your folder (pass a destination to put it elsewhere,
e.g. off the synced drive). Run it again the same day and it won't overwrite — the next
one is `…_02.zip`, then `_03`, and so on. No Python? Snapshot by hand: right-click the
folder → **Compress** (macOS) or **Send to → Compressed (zipped) folder** (Windows).

## Import past chats

Pull the useful bits of your old AI conversations into the wiki — **selectively**, and
**without storing the raw chats**. Claude reads your export where it already sits,
groups the chats by topic, asks which groups to keep, and writes only those distilled
pages into the wiki. The export is never copied into this folder — good, since chat
logs often hold sensitive info. It's a one-time job. Claude reads a lightweight index
(titles + previews), not the whole export, so even a huge history stays manageable.

**Prompt:**

> Ingest my chat history.

**How to point Claude at your chats:**
- **Claude Code (automatic)** — your local sessions in `~/.claude/projects/` are read
  directly; just run the prompt. No export needed.
- **Everything else** — export from the provider, unzip it, then **drag the extracted
  folder (or file) into the chat window** (or paste its path) and run the prompt.
  Nothing gets copied into your second brain.

**Getting the export, per provider:**
- **Claude (web/desktop):** claude.ai → Settings → Account → **Export data** → you get
  an emailed `conversations.json`.
- **ChatGPT:** Settings → **Data controls** → **Export data** → email link → unzip →
  `conversations.json`.
- **Gemini:** [Google Takeout](https://takeout.google.com) → select **Gemini Apps** →
  export → unzip.
- **Perplexity:** Settings → export/download your data (or save individual threads as
  markdown).
- **Others:** any `.json` / `.jsonl` export works; if it's another format and small,
  Claude can read it directly.

Prefer **JSON** exports — the importer indexes JSON/JSONL. A single HTML thread can be
cleaned with defuddle, but large HTML exports flatten badly, so grab JSON where you can.
Unzip the export first (double-click the `.zip`), then drag the folder in.

Indexing a large export runs `chat_import.py`, so do a big import from **Claude Code**
(or another Python-capable env). On a file-only connector, Claude can read a small
export directly but can't index a large one.

## Using Obsidian

Obsidian turns the wiki into a browsable, linked graph. It only reads/renders the
files — Claude still does the writing.

**Install:**
- **macOS:** download from [obsidian.md](https://obsidian.md), open the `.dmg`, drag
  **Obsidian** into **Applications**, and launch it.
- **Windows:** download from [obsidian.md](https://obsidian.md), run the `.exe`
  installer, and launch Obsidian.

**Point it at this folder:** on Obsidian's start screen (or the vault switcher,
bottom-left) choose **Open folder as vault** and select this folder (the one holding
`CLAUDE.md`).
Your pages, `[[wikilinks]]`, and graph view appear immediately.

## Running the Python helpers

`tools/search.py` (wiki search) and `tools/chat_import.py` (chat import) are Python
scripts, so they run only where the agent can execute code — **Claude Code**, or
another setup with a shell/code tool. A plain filesystem connector (Desktop /
claude.ai) can read and write your wiki but can't run scripts; there the wiki still
works — Claude navigates via `index.md` and reads pages directly — you just don't get
scripted search or bulk chat import.

**Check / set up Python — Prompt:**

> Check whether Python 3 can run here (try `python3 --version`, or `python --version`
> on Windows). If it's missing, tell me how to install it for my OS, then confirm
> `python3 tools/search.py --self-test` prints "self-test ok".

**Search:** `python3 tools/search.py "your query"` (Windows: `python …`). Local BM25
over the wiki; the wiki works without it — it just makes a large wiki faster to query.

## Optional add-ons

Cross-platform extras; the core brain works without them. Credited projects are MIT.
Each shows the prompt to paste to Claude to set it up.

### Obsidian Markdown conventions *(bundled — already active)*
`docs/obsidian-markdown.md` makes pages render right in Obsidian on desktop and
mobile. It's already wired into `CLAUDE.md` — nothing to set up. From
[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills).

### defuddle — clean web pages into markdown *(needs Node + a shell, e.g. Claude Code)*
Turns a cluttered article — a URL **or a local `.html` file** — into clean markdown
in `raw/`, ready to ingest. Claude also reaches for it automatically when you ingest
an `.html` file.

**Prompt:**

> Set up defuddle for web capture: check Node.js is installed, run
> `npm install -g defuddle`, then `defuddle parse "<url-or-file.html>" --md -o raw/<slug>.md`
> to save cleaned markdown into `raw/`, and ingest it.

From [kepano/defuddle](https://github.com/kepano/defuddle).

### Obsidian-only extras *(optional)*
JSON Canvas (`.canvas`), Bases (`.base`), and the Obsidian CLI — worth it only if you
work inside Obsidian.

**Prompt:**

> Set up Obsidian Canvas/Bases support: read the relevant skill in
> kepano/obsidian-skills (json-canvas, obsidian-bases, or obsidian-cli) and follow it
> to create a `.canvas` map / `.base` view over my key wiki pages.

From [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills).

**Not bundled:** [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
— a capable framework, but a Python 3.11+ package that needs WSL to write on Windows,
which breaks the extract-and-go, native-on-both-OSes goal. Design reference only.

## Growing it

At ~100 sources / hundreds of pages, `index.md` + `tools/search.py` is enough. If it
grows into thousands of pages, upgrade search to [`qmd`](https://github.com/) (hybrid
BM25 + vector search, CLI + MCP server). Installing and indexing qmd runs shell
commands, so do it from **Claude Code**.

**Prompt:**

> Upgrade the wiki's search to qmd: install the qmd CLI, index `wiki/`, verify it
> returns results, then update the **Search tool** section of `CLAUDE.md` to call qmd
> instead of `tools/search.py`.
