from pathlib import Path

def check_path(path: Path | str) -> Path:
    """Проверяет, что путь существует и возвращает объект Path."""
    if not isinstance(path, (Path, str)):
        raise TypeError("Path must be a string or Path object")

    path = Path(path)

    if not path.exists():
        raise NotADirectoryError(f"Path {path} does not exist")

    return path


def read_gitignore(path: Path) -> list[str]:
    """Читает .gitignore и возвращает список шаблонов для игнорирования."""
    gitignore = path / '.gitignore'
    patterns = []
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8', errors='ignore')
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Убираем завершающие слэши, если это директории
                patterns.append(line.rstrip('/'))
    return patterns


def is_ignored(relative_path: Path, ignore_patterns: list[str]) -> bool:
    """
    Проверяет, должен ли файл быть проигнорирован по списку паттернов .gitignore.
    Поддерживает:
      - data/          → игнорировать всю папку data и её содержимое
      - *.log          → все .log файлы
      - /config.txt    → только в корне
      - **/temp/       → все папки temp в любом месте
    """
    str_path = relative_path.as_posix()  # используем / всегда

    for pattern in (p.strip() for p in ignore_patterns if p.strip()):
        # Убираем завершающий слэш для обработки
        clean_pattern = pattern.rstrip('/')

        # Полный путь с / в начале — только в корне
        if pattern.startswith('/'):
            if str_path == clean_pattern[1:] or str_path.startswith(clean_pattern[1:] + '/'):
                return True

        # Заканчивается на / — это директория, игнорируем всё её содержимое
        elif pattern.endswith('/'):
            if str_path == clean_pattern or str_path.startswith(clean_pattern):
                return True

        # Содержит ** — рекурсивный матч
        elif '**' in pattern:
            import fnmatch
            # Заменяем ** на * для простой проверки (упрощённо)
            # Лучше использовать pathspec, но пока упростим
            if fnmatch.fnmatch(str_path, pattern.replace('**', '*')):
                return True

        # Простой паттерн: *.ext, имя файла
        elif pattern.startswith('*') or pattern.endswith('*'):
            import fnmatch
            if fnmatch.fnmatch(str_path, pattern):
                return True
            if fnmatch.fnmatch(relative_path.name, pattern):
                return True

        # Просто имя файла/папки
        else:
            if relative_path.name == pattern:
                return True
            if str_path.startswith(f"{pattern}/"):  # подпапки
                return True

    return False


def is_text_file(file_path: Path) -> bool:
    """
    Эвристика: определяет, является ли файл текстовым.
    Пробует прочитать первые N байт и проверяет на бинарные данные.
    """
    try:
        with file_path.open('rb') as f:
            chunk = f.read(1024)
            if not chunk:
                return True  # пустой файл — считаем текстовым
            # Если есть много нулевых байтов — вероятно, бинарный
            if b'\x00' in chunk:
                return False
            # Попробуем декодировать
            try:
                chunk.decode('utf-8', errors='replace')
                return True
            except UnicodeDecodeError:
                return False
            return True
    except Exception:
        return False