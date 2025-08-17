# code_to_text

A simple yet powerful tool to convert your entire codebase into a structured text format, making it easy to analyze, archive, or feed into large language models (LLMs) like Qwen, GPT, etc.

## 🚀 Overview

`code_to_text` scans a project directory, identifies text files (source code, configs, scripts, etc.), and exports their contents into individual `.txt` files with a clear header indicating the original file path.

All output files are saved in a structured flat format under a result directory, preserving the original project hierarchy in filenames.

Perfect for:
- Preparing code for ingestion into LLMs
- Creating training datasets
- Code documentation and review
- Archiving project contents in a uniform way

## 📁 Output Format

Each file is saved as:
```
<output_dir>/<relative_path_with_dots>.txt
```

Example:
```
project/
└── src/
    └── main.py
```

Becomes:
```
result/project/src.main.py.txt
```

With content:
```
=== FILE: src/main.py ===
print("Hello, world!")
```

## 🛠️ Usage

```python
extract_text_files(
    repo_path='path/to/your/repo',
    output_dir='path/to/output',  # optional
    user_ignore=['README.md', '*.log'],  # optional additional ignore patterns
    encoding='utf-8'
)
```

If `output_dir` is not specified, the tool creates a folder:
```
./result/<repo_name>/
```

## 🧩 Features

- ✅ Respects `.gitignore` rules
- ✅ Custom ignore patterns via `user_ignore`
- ✅ Skips binary files using heuristic detection
- ✅ Skips hidden files and directories (e.g. `.git/`, `.venv/`)
- ✅ Safe UTF-8 reading with error handling
- ✅ Preserves file structure in output naming
- ✅ Easy integration with LLM workflows

## 📂 Project Structure

```
code_to_text/
├── main.py            # Main script with `extract_text_files`
├── misc.py            # Utilities: path checks, gitignore parsing, file type detection
└── README.md          # This file
```

## 🧪 Example

To process a project and send all code to a `.txt` bundle:

```python
from main import extract_text_files

extract_text_files(
    repo_path='/home/user/my_project',
    user_ignore=['*.md', '__pycache__', 'tests/']
)
```

Output will be saved to:
```
./result/my_project/
```

Each code file will be a `.txt` with its full path embedded.

## 📝 License

MIT License. Feel free to use, modify, and distribute.

---

Made with ❤️ for developers and AI enthusiasts.