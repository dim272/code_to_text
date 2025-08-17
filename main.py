from pathlib import Path

from misc import check_path, read_gitignore, is_ignored, is_text_file


def extract_text_files(
        repo_path: str | Path,
        output_dir: str | Path | None = None,
        user_ignore: list[str] | None = None,
        encoding: str = 'utf-8'
):
    """
    Scans a repository, extracts text from files, and saves them as .txt files
    named <relative_path>.txt in the specified directory.
    If output_dir is not provided, defaults to:
        ./result/<repo_folder_name>/

    :param repo_path: Path to the project root
    :param output_dir: Directory to save .txt files (optional)
    :param user_ignore: Additional files/patterns to ignore
    :param encoding: File encoding for reading (default: utf-8)
    """
    repo_path = check_path(repo_path)
    repo_path = repo_path.resolve()  # Convert to absolute path

    # Use folder name as repo name
    repo_name = repo_path.name or 'unknown_repo'

    # Default output directory: ./result/<repo_name>/
    if output_dir is None:
        output_dir = Path.cwd() / 'result' / repo_name
    else:
        output_dir = Path(output_dir)

    user_ignore = user_ignore or []

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Combine .gitignore patterns and user-defined ones
    gitignore_patterns = read_gitignore(repo_path)
    all_ignore_patterns = gitignore_patterns + user_ignore

    # Recursively scan all files
    for file_path in repo_path.rglob('*'):
        if file_path.is_dir():
            continue

        # Get relative path
        try:
            relative_path = file_path.relative_to(repo_path)
        except ValueError:
            continue  # Skip if not relative (should not happen)

        # Skip hidden directories or files
        if any(part.startswith('.') for part in relative_path.parts):
            continue

        # Skip if matches ignore patterns
        if is_ignored(relative_path, all_ignore_patterns):
            continue

        # Skip binary files
        if not is_text_file(file_path):
            continue

        # Generate safe filename: replace / and \ with ., keep structure
        safe_filename = str(relative_path).replace('/', '.').replace('\\', '.') + '.txt'
        output_file = output_dir / safe_filename

        # Create parent directories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = file_path.read_text(encoding=encoding, errors='replace')
            output_file.write_text(
                f"=== FILE: {relative_path} ===\n\n{content}\n\n",
                encoding=encoding,
                errors='ignore'
            )
            print(f"Saved: {output_file}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")


if __name__ == '__main__':
    extract_text_files(
        repo_path='',                   # e.g., /home/user/project
        user_ignore=['README.md']       # additional files to ignore
    )
