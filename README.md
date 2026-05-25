# wordfreqx

`wordfreqx` counts and ranks words in text files or stdin.

## Install

```bash
pip install wordfreqx
```

## Use

```bash
wordfreqx notes.txt
wordfreqx docs/ --ignore-stopwords --top 20
cat notes.txt | wordfreqx --json
```

## Features

- text files, dirs, stdin
- top-N word stats
- min length filter
- stopword filtering
- JSON output

## Dev

```bash
python -m pip install -e . pytest
pytest
```
