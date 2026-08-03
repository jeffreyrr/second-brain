#!/usr/bin/env python3
"""Index and extract conversations from LLM chat exports, so Claude can ingest
them *selectively*. Stdlib only, mac + windows.

The point: an export can be thousands of chats / tens of MB — too big to read
into a chat. `index` reduces it to one line per conversation (title, date, size,
preview) so Claude can group by topic and ask which groups you want. `show` then
prints the full text of only the conversations you chose.

Commands:
    python3 tools/chat_import.py index <path> [--json]   # list conversations
    python3 tools/chat_import.py show  <path> <id>        # full transcript of one
    python3 tools/chat_import.py --self-test

<path> may be a file or a folder. Supported formats:
  - ChatGPT            conversations.json
  - Claude.ai export   conversations.json  (web / desktop "Export data")
  - Claude Code        session .jsonl files (e.g. ~/.claude/projects/**/*.jsonl)
Other providers (Gemini, Perplexity, …): convert the export to JSON, or if it's
small just let Claude read the file directly.

# ponytail: json.load holds the whole export in memory — fine to ~100MB; stream if bigger.
"""
import argparse
import json
import sys
import time
from pathlib import Path


def _date(v):
    """Normalize an epoch float or ISO string to YYYY-MM-DD; '' if unknown."""
    if isinstance(v, (int, float)):
        return time.strftime("%Y-%m-%d", time.gmtime(v))
    if isinstance(v, str) and len(v) >= 10:
        return v[:10]
    return ""


def _text(content):
    """Pull plain text from a str, a list of blocks, or ChatGPT parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for b in content:
            if isinstance(b, str):
                out.append(b)
            elif isinstance(b, dict) and b.get("type", "text") == "text":
                out.append(b.get("text", ""))
        return "\n".join(t for t in out if t)
    return ""


def _conv(provider, cid, title, date, messages, source):
    return {"provider": provider, "id": str(cid), "title": title or "(untitled)",
            "date": date, "messages": messages, "source": str(source)}


def parse_chatgpt(data, source):
    convs = []
    for i, c in enumerate(data):
        nodes = [n["message"] for n in c.get("mapping", {}).values() if n.get("message")]
        nodes.sort(key=lambda m: m.get("create_time") or 0)
        msgs = []
        for m in nodes:
            role = (m.get("author") or {}).get("role", "?")
            txt = _text((m.get("content") or {}).get("parts", []))
            if txt.strip():
                msgs.append({"role": role, "text": txt})
        convs.append(_conv("chatgpt", c.get("id") or c.get("conversation_id") or f"cg-{i}",
                            c.get("title"), _date(c.get("create_time")), msgs, source))
    return convs


def parse_claude_ai(data, source):
    convs = []
    for i, c in enumerate(data):
        msgs = []
        for m in c.get("chat_messages", []):
            role = "user" if m.get("sender") == "human" else (m.get("sender") or "assistant")
            txt = m.get("text") or _text(m.get("content", []))
            if txt.strip():
                msgs.append({"role": role, "text": txt})
        convs.append(_conv("claude", c.get("uuid") or f"cl-{i}", c.get("name"),
                           _date(c.get("created_at")), msgs, source))
    return convs


def parse_claude_code(path):
    """One .jsonl file = one Claude Code session."""
    msgs, date, title = [], "", None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") == "summary" and not title:
            title = o.get("summary")
        m = o.get("message")
        if o.get("type") in ("user", "assistant") and isinstance(m, dict):
            txt = _text(m.get("content", ""))
            if txt.strip():
                msgs.append({"role": m.get("role", o["type"]), "text": txt})
                date = date or _date(o.get("timestamp"))
    if not title and msgs:
        title = msgs[0]["text"][:60]
    return [_conv("claude-code", Path(path).stem, title, date, msgs, path)] if msgs else []


def load(path):
    p = Path(path).expanduser()
    if not p.exists():
        sys.exit(f"not found: {p}")
    convs = []
    if p.is_dir():
        for f in sorted(p.rglob("*.jsonl")):
            convs += parse_claude_code(f)
        for f in sorted(p.rglob("*.json")):
            convs += _load_json(f)
        return convs
    if p.suffix == ".jsonl":
        return parse_claude_code(p)
    if p.suffix == ".json":
        return _load_json(p)
    sys.exit(f"unsupported file (need .json or .jsonl): {p}")


def _load_json(f):
    try:
        data = json.loads(Path(f).read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list) or not data:
        return []
    sample = data[0]
    if isinstance(sample, dict) and "mapping" in sample:
        return parse_chatgpt(data, f)
    if isinstance(sample, dict) and ("chat_messages" in sample or ("name" in sample and "uuid" in sample)):
        return parse_claude_ai(data, f)
    return []


def cmd_index(convs, as_json):
    if as_json:
        rows = [{"provider": c["provider"], "id": c["id"], "title": c["title"],
                 "date": c["date"], "n_messages": len(c["messages"]),
                 "chars": sum(len(m["text"]) for m in c["messages"]),
                 "preview": c["messages"][0]["text"][:140] if c["messages"] else ""}
                for c in convs]
        print(json.dumps(rows, indent=2))
        return
    if not convs:
        print("no conversations found")
        return
    print(f"{len(convs)} conversations\n")
    for c in convs:
        kb = sum(len(m["text"]) for m in c["messages"]) // 1000
        preview = (c["messages"][0]["text"][:100].replace("\n", " ") if c["messages"] else "")
        print(f"[{c['provider']:11}] {c['date'] or '----------'}  {len(c['messages']):3}msg {kb:4}kb  {c['title'][:60]}")
        print(f"    id={c['id']}")
        print(f"    {preview}")


def cmd_show(convs, cid):
    for c in convs:
        if c["id"] == cid:
            print(f"# {c['title']}  ({c['provider']}, {c['date']})\n")
            for m in c["messages"]:
                print(f"## {m['role']}\n{m['text']}\n")
            return
    sys.exit(f"id not found: {cid}  ({len(convs)} conversations in that path)")


def self_test():
    cg = [{"title": "Rust vs Go", "create_time": 1700000000,
           "mapping": {"1": {"message": {"author": {"role": "user"},
                       "content": {"parts": ["which is faster?"]}, "create_time": 1}}}}]
    assert parse_chatgpt(cg, "x")[0]["title"] == "Rust vs Go"
    assert parse_chatgpt(cg, "x")[0]["messages"][0]["text"] == "which is faster?"
    cl = [{"uuid": "u1", "name": "Tax questions", "created_at": "2026-01-02T03:04:05Z",
           "chat_messages": [{"sender": "human", "text": "deductible?"}]}]
    assert parse_claude_ai(cl, "x")[0]["date"] == "2026-01-02"
    assert parse_claude_ai(cl, "x")[0]["messages"][0]["role"] == "user"
    assert _text([{"type": "text", "text": "a"}, {"type": "tool_use"}]) == "a"
    assert _date(1700000000).startswith("20")
    print("self-test ok")


def main():
    ap = argparse.ArgumentParser(description="Index/extract LLM chat exports.")
    ap.add_argument("command", nargs="?", choices=["index", "show"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("id", nargs="?")
    ap.add_argument("--json", action="store_true", help="index: machine-readable output")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.command or not args.path:
        ap.error("usage: index <path> [--json] | show <path> <id> | --self-test")
    convs = load(args.path)
    if args.command == "index":
        cmd_index(convs, args.json)
    else:
        if not args.id:
            ap.error("show needs an <id> (get it from `index`)")
        cmd_show(convs, args.id)


if __name__ == "__main__":
    main()
