#!/usr/bin/env python3
"""BM25 search over the wiki's markdown. Stdlib only, mac + windows.

Usage:
    python3 tools/search.py "your query"        # ranked pages + snippet
    python3 tools/search.py "query" -n 20        # top 20 (default 10)
    python3 tools/search.py "query" --wiki PATH  # search a different dir
    python3 tools/search.py --self-test          # sanity check, no wiki needed

Wiki dir defaults to ../wiki relative to this script, so it works from any cwd
and on either OS. qmd is the upgrade path once this outgrows plain BM25 — see CLAUDE.md.
"""
import argparse
import math
import re
import sys
from pathlib import Path

WORD = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return WORD.findall(text.lower())


def bm25(query_tokens, docs, k1=1.5, b=0.75):
    """docs: list of (id, tokens). Returns [(id, score)] sorted desc, score>0 only."""
    n = len(docs)
    if n == 0:
        return []
    avg_len = sum(len(t) for _, t in docs) / n
    # document frequency per query term
    df = {}
    for term in set(query_tokens):
        df[term] = sum(1 for _, toks in docs if term in toks)
    scores = []
    for doc_id, toks in docs:
        freq = {}
        for t in toks:
            freq[t] = freq.get(t, 0) + 1
        score = 0.0
        dl = len(toks)
        for term in query_tokens:
            f = freq.get(term, 0)
            if f == 0 or df.get(term, 0) == 0:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avg_len))
        if score > 0:
            scores.append((doc_id, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def load_docs(wiki_dir):
    docs, texts = [], {}
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.name in ("index.md", "log.md"):
            continue  # navigation/meta, not content — keep them out of results
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(wiki_dir).as_posix()
        docs.append((rel, tokenize(text)))
        texts[rel] = text
    return docs, texts


def snippet(text, query_tokens, width=160):
    lower = text.lower()
    for term in query_tokens:
        i = lower.find(term)
        if i != -1:
            start = max(0, i - width // 2)
            frag = text[start:start + width].replace("\n", " ").strip()
            return ("…" if start else "") + frag + "…"
    return text.strip().replace("\n", " ")[:width]


def self_test():
    docs = [
        ("a", tokenize("attention transformer neural network")),
        ("b", tokenize("transformer language model attention attention")),
        ("c", tokenize("banana bread recipe")),
    ]
    ranked = bm25(tokenize("attention transformer"), docs)
    ids = [d for d, _ in ranked]
    assert ids[:2] == ["b", "a"], ids           # b outranks a (more matches)
    assert "c" not in ids, ids                   # no overlap -> excluded
    assert bm25(tokenize("nothing"), docs) == []
    assert bm25(tokenize("x"), []) == []         # empty corpus
    print("self-test ok")


def main():
    ap = argparse.ArgumentParser(description="BM25 search over the wiki.")
    ap.add_argument("query", nargs="*", help="search terms")
    ap.add_argument("-n", type=int, default=10, help="max results (default 10)")
    ap.add_argument("--wiki", default=None, help="wiki dir (default ../wiki)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if not args.query:
        ap.error("give a query, or --self-test")

    wiki_dir = Path(args.wiki) if args.wiki else Path(__file__).resolve().parent.parent / "wiki"
    if not wiki_dir.is_dir():
        sys.exit(f"wiki dir not found: {wiki_dir}")

    q = tokenize(" ".join(args.query))
    docs, texts = load_docs(wiki_dir)
    ranked = bm25(q, docs)[: args.n]
    if not ranked:
        print("no matches")
        return
    for rel, score in ranked:
        print(f"{score:6.2f}  {rel}")
        print(f"        {snippet(texts[rel], q)}")


if __name__ == "__main__":
    main()
