from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

WORD_RE = re.compile(r"[A-Za-z0-9']+")
DEFAULT_STOPWORDS = {"the", "and", "a", "to", "of", "in", "is", "it", "for", "on", "with", "as", "at", "by"}


def iter_words(text: str, min_length: int = 1) -> Iterable[str]:
    for raw in WORD_RE.findall(text.lower()):
        if len(raw) >= min_length:
            yield raw


def load_texts(paths: list[str]) -> list[tuple[str, str]]:
    if not paths:
        return [("<stdin>", sys.stdin.read())]
    items: list[tuple[str, str]] = []
    for arg in paths:
        path = Path(arg)
        if path.is_dir():
            for child in sorted(path.rglob("*.txt")):
                items.append((str(child), child.read_text(encoding="utf-8")))
        else:
            if not path.exists():
                raise FileNotFoundError(arg)
            items.append((str(path), path.read_text(encoding="utf-8")))
    return items


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wordfreqx", description="Count and rank words in text files.")
    p.add_argument("paths", nargs="*", help="Text files or directories. Reads stdin when omitted.")
    p.add_argument("--top", type=int, default=10, help="Max entries to show.")
    p.add_argument("--min-length", type=int, default=1, help="Ignore shorter words.")
    p.add_argument("--json", action="store_true", help="Emit JSON.")
    p.add_argument("--ignore-stopwords", action="store_true", help="Drop common stopwords.")
    p.add_argument("--stopwords", type=Path, help="Extra stopwords file, one word per line.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        texts = load_texts(args.paths)
    except FileNotFoundError as exc:
        print(f"missing file: {exc.args[0]}", file=sys.stderr)
        return 2

    stopwords = set(DEFAULT_STOPWORDS) if args.ignore_stopwords else set()
    if args.stopwords:
        stopwords |= {line.strip().lower() for line in args.stopwords.read_text(encoding="utf-8").splitlines() if line.strip()}

    counts: Counter[str] = Counter()
    files: list[dict[str, object]] = []
    for name, text in texts:
        words = list(iter_words(text, max(args.min_length, 1)))
        filtered = [w for w in words if w not in stopwords]
        counts.update(filtered)
        files.append({"path": name, "words": len(filtered), "unique": len(set(filtered))})

    top = counts.most_common(max(args.top, 1))
    if args.json:
        print(json.dumps({"files": files, "top": [{"word": w, "count": c} for w, c in top]}, indent=2))
    else:
        for item in files:
            print(f"{item['path']}: words={item['words']} unique={item['unique']}")
        print("top:")
        for word, count in top:
            print(f"  {word} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
