from pathlib import Path

from misc import check_path, read_gitignore, is_ignored, is_text_file


def extract_text_files(
        repo_path: str | Path,
        output_dir: str | Path | None = None,
        user_ignore: list[str] | None = None,
        encoding: str = 'utf-8'
):
    """
    Сканирует репозиторий, извлекает текст из файлов и сохраняет их как .txt
    с именем <относительный_путь>.txt в указанной директории.

    Если output_dir не указан, используется:
        ./result/<имя_папки_repo_path>/

    :param repo_path: Путь к корню проекта
    :param output_dir: Куда сохранять .txt файлы (опционально)
    :param user_ignore: Дополнительные файлы/паттерны для игнорирования
    :param encoding: Кодировка для чтения файлов
    """
    repo_path = check_path(repo_path)
    repo_path = repo_path.resolve()  # Полный путь, без относительностей

    # Определяем имя папки репозитория
    repo_name = repo_path.name or 'unknown_repo'

    # Автоматический output_dir: ./result/<repo_name>/
    if output_dir is None:
        output_dir = Path.cwd() / 'result' / repo_name
    else:
        output_dir = Path(output_dir)

    user_ignore = user_ignore or []

    # Создаём выходную директорию
    output_dir.mkdir(parents=True, exist_ok=True)

    # Собираем паттерны игнорирования
    gitignore_patterns = read_gitignore(repo_path)
    all_ignore_patterns = gitignore_patterns + user_ignore

    # Проходим по всем файлам рекурсивно
    for file_path in repo_path.rglob('*'):
        if file_path.is_dir():
            continue

        # Получаем относительный путь
        try:
            relative_path = file_path.relative_to(repo_path)
        except ValueError:
            continue  # на всякий случай

        # Проверяем, находится ли файл в скрытой директории
        if any(part.startswith('.') for part in file_path.relative_to(repo_path).parts) or \
                is_ignored(relative_path, all_ignore_patterns):
            continue

        # Проверяем, текстовый ли файл
        if not is_text_file(file_path):
            continue

        # Формируем имя выходного файла: some/path/file.py.txt
        # Заменяем / и \ на ., сохраняем структуру в имени файла
        safe_filename = str(relative_path).replace('/', '.').replace('\\', '.') + '.txt'
        output_file = output_dir / safe_filename

        # Создаём родительскую директорию для выходного файла
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
        repo_path='',                   # /home/user/project
        user_ignore=['README.md',]      # ignored files
    )
