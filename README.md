# code2doc

`code2doc` is a lightweight Python tool to automatically generate `.docx` assignment files from your source code.\
It scans your project folder, picks up specified files, and formats them neatly into a Word document — perfect for uploading or submitting coursework without copy-pasting code a million times.

## ✨ Features
- 🚀 Automatically traverses your project folder (using os.walk)
- 📂 Collects .java files (configurable to other languages like .py, .cpp, etc.)
- 📝 Exports your code into a clean, readable DOCX file
- 🔠 Custom fonts & formatting for code blocks
- 🏷️ Adds headings for each file and subdirectory
- 📌 Optional cover page / header / footer
- 🔗 Supports clickable GitHub links inside the document

<!-- 
## Usage

```bash
code2doc generate --input ./src --output ./docs
```

### Options

- `--input`: Path to your source code directory
- `--output`: Output directory for generated docs
- `--format`: Output format (`markdown`, `html`, `pdf`) -->

<!-- ## Example

```bash
code2doc generate --input ./my_project --output ./my_project_docs --format html
``` -->

## 🛠️ Installation

This project uses [uv](https://docs.astral.sh/uv/getting-started/installation/) as the Python package manager.

```bash
git clone https://www.github.com/anshulbadhani/code2doc
cd code2doc
```

## ⚙️Usage
1. Make a `config.json` file.
2. Paste the contents from `sample_config_file.json`.
3. Edit the fields accordingly.
4. Run the python script using:
    ```bash
    uv run main.py
    ```

## 📁Project Structure
```txt
code2doc/
├── main.py                 # Entry point script
├── config.json             # Active project configuration (your paths & extensions)
├── sample_config_file.json # Example config template
├── pyproject.toml          # Project metadata & dependencies (uv format)
├── uv.lock                 # Lockfile for uv dependency versions
└── README.md               # Project documentation

```

---
