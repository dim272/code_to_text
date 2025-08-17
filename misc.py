from pathlib import Path


def check_path(path: Path | str) -> Path:
    """Checks that the path exists and returns a Path object."""
    if not isinstance(path, (Path, str)):
        raise TypeError("Path must be a string or Path object")
    path = Path(path)
    if not path.exists():
        raise NotADirectoryError(f"Path {path} does not exist")
    return path


def read_gitignore(path: Path) -> list[str]:
    """Reads .gitignore and returns a list of ignore patterns."""
    gitignore = path / '.gitignore'
    patterns = []
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8', errors='ignore')
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove trailing slashes if present (for directories)
                patterns.append(line.rstrip('/'))
    return patterns


def is_ignored(relative_path: Path, ignore_patterns: list[str]) -> bool:
    """
    Checks if a file should be ignored based on .gitignore-like patterns.
    Supports:
      - data/          → ignore entire 'data' folder and its contents
      - *.log          → all .log files
      - /config.txt    → only in root
      - **/temp/       → any 'temp' folder anywhere in the structure
    """
    str_path = relative_path.as_posix()  # Always use forward slashes
    for pattern in (p.strip() for p in ignore_patterns if p.strip()):
        clean_pattern = pattern.rstrip('/')  # Remove trailing slash
        # Starts with / → match only in root
        if pattern.startswith('/'):
            if str_path == clean_pattern[1:] or str_path.startswith(clean_pattern[1:] + '/'):
                return True
        # Ends with / → directory and all its contents
        elif pattern.endswith('/'):
            if str_path == clean_pattern or str_path.startswith(clean_pattern):
                return True
        # Contains ** → recursive match
        elif '**' in pattern:
            import fnmatch
            # Replace ** with * for simplified matching (basic approximation)
            # For full compliance, use 'pathspec', but this is simpler
            if fnmatch.fnmatch(str_path, pattern.replace('**', '*')):
                return True
        # Wildcard patterns: *.ext, *name, etc.
        elif pattern.startswith('*') or pattern.endswith('*'):
            import fnmatch
            if fnmatch.fnmatch(str_path, pattern):
                return True
            if fnmatch.fnmatch(relative_path.name, pattern):
                return True
        # Plain filename or folder name
        else:
            if relative_path.name == pattern:
                return True
            if str_path.startswith(f"{pattern}/"):  # Subdirectories
                return True
    return False


def is_text_file(file_path: Path) -> bool:
    """
    Heuristic: determines if a file is a text file.
    Tries to read the first N bytes and checks for binary data.
    """
    try:
        with file_path.open('rb') as f:
            chunk = f.read(1024)
            if not chunk:
                return True  # Empty file → treat as text
            # If there are many null bytes, likely binary
            if b'\x00' in chunk:
                return False
            # Try to decode as UTF-8
            try:
                chunk.decode('utf-8', errors='replace')
                return True
            except UnicodeDecodeError:
                return False
    except Exception:
        return False
