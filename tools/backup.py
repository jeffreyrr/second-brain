#!/usr/bin/env python3
"""Snapshot the whole second brain into a timestamped .zip — a restore point before
a big change. Stdlib only, mac + windows. Needs Python (e.g. Claude Code).

    python3 tools/backup.py              # -> ../<folder>-backup-YYYY-MM-DD.zip
    python3 tools/backup.py <dest-dir>   # write the zip somewhere else
    python3 tools/backup.py --self-test

Same-day repeats don't clobber: the first is …-YYYY-MM-DD.zip, the next …_02.zip, _03, …

By default the zip lands OUTSIDE the brain folder (next to it), so backups don't pile
up inside it. Your cloud sync (Drive/Dropbox) already keeps per-file version history;
this is for full snapshots you control. Pass a dest-dir off the synced drive (e.g.
~/Desktop) if you'd rather the zip not sync.
"""
import shutil
import sys
import time
from pathlib import Path


def _next_base(dest_dir, stem):
    """First of the day is <stem> (no number); later ones are <stem>_02, _03, …"""
    if not (dest_dir / f"{stem}.zip").exists():
        return dest_dir / stem
    n = 2
    while (dest_dir / f"{stem}_{n:02d}.zip").exists():
        n += 1
    return dest_dir / f"{stem}_{n:02d}"


def backup(root, dest_dir):
    root = Path(root).resolve()
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    base = _next_base(dest_dir, f"{root.name}-backup-{time.strftime('%Y-%m-%d')}")
    # base_dir=root.name so the zip contains the folder itself (paths stay relative);
    # only that folder is archived, so a zip sitting in the parent isn't swept in.
    out = shutil.make_archive(str(base), "zip", root_dir=str(root.parent), base_dir=root.name)
    return Path(out)


def self_test():
    import tempfile
    import zipfile
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        brain = d / "brain"
        (brain / "wiki").mkdir(parents=True)
        (brain / "wiki" / "a.md").write_text("hi", encoding="utf-8")
        out = backup(brain, d / "out")
        assert out.exists() and out.suffix == ".zip", out
        assert not out.stem.endswith("_02"), out          # first of the day: no number
        names = zipfile.ZipFile(out).namelist()
        assert any(n.endswith("wiki/a.md") for n in names), names
        out2 = backup(brain, d / "out")                    # same day again -> _02
        assert out2.stem.endswith("_02") and out2 != out, out2
    print("self-test ok")


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        self_test()
        return
    root = Path(__file__).resolve().parent.parent   # tools/ -> root
    dest = args[0] if args else str(root.parent)
    print(f"backed up to {backup(root, dest)}")


if __name__ == "__main__":
    main()
