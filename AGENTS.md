# AGENTS.md — code2doc

Single-file Python CLI (`main.py`) that scans a directory for code files and bundles them into a `.docx`. Managed with `uv`. Python 3.12+.

## Run it

```bash
uv run main.py                 # uses config.json for defaults
uv run main.py --help          # all flags
```

`main.py` reads `config.json` (and optionally `.credits.json`) at startup to fill defaults. `root_dir` is a positional argument; everything else is a `--flag` overriding the config.

Key flags: `--ordered`/`-o` (natural sort, e.g. 1,2,10), `--number`/`-num`, `--ext`/`-e` (repeatable), `--name`, `--heading`, `--code-font`, `--gitignore/--no-gitignore`, plus footer options (`--project-name`, `--github-link`, `--author`).

**`.gitignore` filtering is on by default.** `main.py` loads every `.gitignore` under `root_dir` (patterns relative to each file's directory) and skips matched files before they reach the docx. `--no-gitignore` disables it. Skipped files print a count, e.g. `⏭️  Skipped 2 file(s) matched by .gitignore`. Uses `pathspec` (gitwildmatch) so `**`, `!` negation, and trailing-slash directory patterns all work like git.

## Config & gitignore traps

- `config.json` is **gitignored** — it holds the user's personal paths. Never commit it; copy from `sample_config_file.json` to create it.
- `.credits.json` is **not** gitignored; it supplies `project_name`/`github_link` for the footer.
- `dist/` (output) and `test.py` are gitignored. Generated `.docx` lands in `dist/` by default.

## Environment

- Install: `uv sync` (deps: `python-docx`, `typer`, `pathspec`).
- `.python-version` pins 3.12; `pyproject.toml` requires `>=3.12`.
- CI (`.github/workflows/python-publish.yml`) runs on `master` using Python 3.13.3 and executes `flake8` + `pytest` — but **no tests exist in the repo**. Don't be surprised if `pytest` finds nothing; the CI step is aspirational, not enforced locally.

## Code structure

Single file: `main.py` (CLI + docx assembly + `.gitignore` matching). Flow: load config → walk `root_dir` filtering by extension → drop `.gitignore`-matched files → optionally natural-sort → build `python-docx` Document → save to `output_dir/output_name.docx`. Errors reading a file are skipped with a warning; a `PermissionError` on save prompts you to close the file.

## Gotchas

- Output filename: pass `--name` with or without `.docx`; the tool appends it if missing.
- `%number%` in `output_file_name`/`heading`/`root_dir` is replaced by `--number`.
- Sorting only applies when `--ordered` is passed; default order is `os.walk` order (arbitrary).
- The `--ext` default is `.cpp` in code but `.java/.py/.js` in the sample config — set it explicitly if your files differ.