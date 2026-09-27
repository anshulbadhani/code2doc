import os
import json
import typer
import re
from typing import List, Optional
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime

import pathspec

# --- 1. Load Configuration Defaults ---
CONFIG_FILE = "config.json"
CREDITS_FILE = ".credits.json"

DEFAULTS = {
    "root_dir": ".",
    "output_dir": "dist",
    "output_file_name": "Assignment_%number%",
    "heading": "Assignment %number%",
    "include_extensions": [".cpp"],
    "code_font": "Courier New",
    "gitignore": True,  # honor .gitignore when scanning
    "project_name": "code2doc", # for credits
    "github_link": "https://github.com/anshulbadhani/code2doc", # for credits
    "author": "Anshul Badhani", # for credits
}

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            DEFAULTS.update(json.load(f))
    except Exception:
        print(f"⚠️ Warning: Could not parse {CONFIG_FILE}.")

if os.path.exists(CREDITS_FILE):
    try:
        with open(CREDITS_FILE, "r") as f:
            DEFAULTS.update(json.load(f))
    except Exception:
        pass

app = typer.Typer(add_completion=False)


# --- Helper: Natural Sorting ---
def natural_sort_key(path: Path):
    """
    Splits a string into text and numbers to sort naturally.
    e.g. converts ["1.cpp", "10.cpp", "2.cpp"] -> ["1.cpp", "2.cpp", "10.cpp"]
    """
    # We sort based on the filename primarily
    s = str(path.name)
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]


# --- Helper: Gitignore Matching ---
def load_gitignore_specs(root: Path):
    """Return [(base_dir, spec), ...] for every .gitignore under `root`.

    Patterns in each file are relative to that file's directory, mirroring git.
    """
    specs = []
    root = Path(root)
    for dirpath, _, filenames in os.walk(root):
        if ".gitignore" in filenames:
            base = Path(dirpath)
            try:
                lines = (base / ".gitignore").read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
            if spec.patterns:
                specs.append((base, spec))
    return specs


def is_ignored(file_path: Path, specs) -> bool:
    """Return True if `file_path` matches any of the loaded gitignore specs."""
    file_path = Path(file_path)
    for base, spec in specs:
        try:
            rel = file_path.relative_to(base)
        except ValueError:
            continue
        if spec.match_file(str(rel)):
            return True
    return False


@app.command()
def main(
    # New Flag for Ordering
    ordered: bool = typer.Option(
        False,
        "--ordered",
        "-o",
        help="Sort files naturally (e.g., 1.cpp, 2.cpp, 10.cpp) before adding to DOCX.",
    ),
    # Existing Arguments
    number: str = typer.Option(None, "--number", "-num", help="Assignment number."),
    root_dir: Optional[Path] = typer.Argument(None, help="Root directory."),
    output_dir: Path = typer.Option(DEFAULTS["output_dir"], help="Output directory."),
    output_name: str = typer.Option(
        DEFAULTS["output_file_name"], "--name", help="Output filename."
    ),
    heading: str = typer.Option(DEFAULTS["heading"], help="Document heading."),
    extensions: List[str] = typer.Option(
        DEFAULTS["include_extensions"], "--ext", "-e", help="Extensions."
    ),
    code_font: str = typer.Option(DEFAULTS["code_font"], help="Code font."),
    gitignore: bool = typer.Option(
        DEFAULTS["gitignore"],
        "--gitignore/--no-gitignore",
        help="Skip files matched by .gitignore under the root directory.",
    ),
    project_name: str = typer.Option(
        DEFAULTS.get("project_name", "Project"), help="Footer project."
    ),
    github_link: str = typer.Option(
        DEFAULTS.get("github_link", ""), help="Footer link."
    ),
    author: str = typer.Option(
        DEFAULTS.get("author", "Anshul Badhani"), help="Footer author."
    ),
):
    """
    Compiles code into DOCX. Use -o to sort files naturally (1, 2, 10).
    Files matched by .gitignore under the root directory are skipped by default
    (use --no-gitignore to include them).
    """

    # --- 1. Setup Paths & Replacements ---
    target_root_str = str(root_dir) if root_dir else str(DEFAULTS["root_dir"])

    if number:
        target_root_str = target_root_str.replace("%number%", number)
        output_name = output_name.replace("%number%", number)
        heading = heading.replace("%number%", number)
        typer.secho(
            f"ℹ️  Assignment {number}: Sorting {'ON' if ordered else 'OFF'}",
            fg=typer.colors.CYAN,
        )

    target_root = Path(target_root_str)

    if not target_root.exists():
        typer.secho(
            f"❌ Error: Directory '{target_root}' does not exist.", fg=typer.colors.RED
        )
        raise typer.Exit(1)

    # Handle output filename
    if output_name.lower().endswith(".docx"):
        OUTPUT_FILE = output_dir / output_name
    else:
        OUTPUT_FILE = output_dir / f"{output_name}.docx"

    output_dir.mkdir(parents=True, exist_ok=True)

    # --- 2. Collect & Sort Files ---
    collected_files = []
    ignored_count = 0
    gitignore_specs = load_gitignore_specs(target_root) if gitignore else []

    typer.echo("🔍 Scanning files...")
    for folder, _, files in os.walk(target_root):
        for filename in files:
            if any(filename.endswith(ext) for ext in extensions):
                full_path = Path(folder) / filename
                if gitignore and is_ignored(full_path, gitignore_specs):
                    ignored_count += 1
                    continue
                collected_files.append(full_path)

    if gitignore and ignored_count:
        typer.secho(
            f"⏭️  Skipped {ignored_count} file(s) matched by .gitignore",
            fg=typer.colors.YELLOW,
        )

    if not collected_files:
        typer.secho(f"❌ No files found in {target_root}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # APPLY SORTING HERE
    if ordered:
        collected_files.sort(key=natural_sort_key)
        typer.echo("✅ Files sorted naturally.")

    # --- 3. Create Document ---
    doc = Document()
    title = doc.add_heading(heading, level=0)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    doc.add_heading("Output at the end", level=2)
    # --- 4. Write Content ---
    for file_path in collected_files:
        rel_path = file_path.relative_to(target_root)

        # Add Header
        doc.add_heading(f"File: {rel_path}", level=2)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            typer.secho(
                f"⚠️ Error reading {file_path.name}: {e}", fg=typer.colors.YELLOW
            )
            continue

        para = doc.add_paragraph(content)
        para.style.font.name = code_font  # type: ignore
        for run in para.runs:
            run.font.size = Pt(10)

    doc.add_heading("Output:", level=2)

    doc.add_section()

    # --- 5. Footer ---
    section = doc.sections[-1]
    footer = section.footer
    footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()

    current_year = datetime.now().year
    footer_text = f"© {current_year} {author} – {project_name} – {github_link}"
    footer_para.text = footer_text
    footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    if footer_para.runs:
        footer_para.runs[0].font.size = Pt(10)

    try:
        doc.save(OUTPUT_FILE)  # type: ignore
        typer.secho(f"✅ Saved: {OUTPUT_FILE}", fg=typer.colors.GREEN)
    except PermissionError:
        typer.secho(
            f"❌ Error: Close the file '{OUTPUT_FILE}' and try again.",
            fg=typer.colors.RED,
        )


if __name__ == "__main__":
    app()
