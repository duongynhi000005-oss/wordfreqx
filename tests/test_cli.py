from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreqx", *args],
        cwd=ROOT,
        text=True,
        input=input_text,
        capture_output=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src")},
    )


def test_text_summary(tmp_path: Path) -> None:
    p = tmp_path / "doc.txt"
    p.write_text("Alpha beta beta\nThe beta!", encoding="utf-8")

    result = run_cli(str(p), "--ignore-stopwords")

    assert result.returncode == 0
    assert "words=4" in result.stdout
    assert "beta 3" in result.stdout


def test_json_stdin() -> None:
    result = run_cli("--json", input_text="one two two three")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["files"][0]["path"] == "<stdin>"
    assert payload["top"][0] == {"word": "two", "count": 2}


def test_min_length_and_missing(tmp_path: Path) -> None:
    p = tmp_path / "tiny.txt"
    p.write_text("a aa aaa", encoding="utf-8")

    ok = run_cli(str(p), "--min-length", "2")
    assert ok.returncode == 0
    assert "words=2" in ok.stdout

    bad = run_cli(str(tmp_path / "nope.txt"))
    assert bad.returncode == 2
    assert "missing file" in bad.stderr
