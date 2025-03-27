import os
from colorama import Fore, Style, init

init(autoreset=True)

TARGET_EXTENSIONS = {".py", ".cs", ".cpp", ".js", ".ts", ".lua"}
FILTER_FILE = ".filter"


def load_excluded_dirs():
    if not os.path.exists(FILTER_FILE):
        return set()
    with open(FILTER_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip().lstrip('.') for line in f if line.strip())


def is_excluded(path, excluded_dirs):
    normalized = os.path.normpath(path).split(os.sep)
    return any(dir_name in normalized for dir_name in excluded_dirs)


def collect_files(root_dir, excluded_dirs):
    collected = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if is_excluded(dirpath, excluded_dirs):
            continue
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]  # prune
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext in TARGET_EXTENSIONS:
                collected.append(os.path.join(dirpath, filename))
    return collected


def analyze_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            return len(lines), len(content)
    except Exception as e:
        print(f"{Fore.RED}Ошибка при чтении {filepath}: {e}")
        return 0, 0


def generate_report(file_stats, report_path='report.md'):
    total_files = len(file_stats)
    total_lines = sum(stats[0] for stats in file_stats.values())
    total_chars = sum(stats[1] for stats in file_stats.values())

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Отчёт по анализу файлов\n\n")
        f.write(f"**Файлов:** {total_files}  |  **Строк:** {total_lines}  |  **Символов:** {total_chars}\n\n")
        f.write("| Файл | Строк | Символов |\n")
        f.write("|------|-------|----------|\n")
        for path, (lines, chars) in file_stats.items():
            f.write(f"| {path} | {lines} | {chars} |\n")

    print(f"{Fore.CYAN}Markdown-отчёт сохранён в {report_path}")


def main():
    excluded_dirs = load_excluded_dirs()
    print(f"{Fore.YELLOW}Сканируем директорию 'inside'...")
    print(f"{Fore.LIGHTBLACK_EX}Игнорируем директории: {excluded_dirs}\n")

    files = collect_files('inside', excluded_dirs)

    if not files:
        print(f"{Fore.RED}Нет подходящих файлов в папке 'inside'")
        return

    file_stats = {}
    for file in files:
        lines, chars = analyze_file(file)
        file_stats[file] = (lines, chars)
        print(f"{Fore.GREEN}{file} {Style.RESET_ALL}| Строк: {lines} | Символов: {chars}")

    total_lines = sum(v[0] for v in file_stats.values())
    total_chars = sum(v[1] for v in file_stats.values())
    print(f"\n{Fore.BLUE}Итог — файлов: {len(file_stats)} | строк: {total_lines} | символов: {total_chars}")

    generate = input(f"\n{Fore.MAGENTA}Создать отчёт в .md? (y/n): ").strip().lower()
    if generate == 'y':
        generate_report(file_stats)


if __name__ == '__main__':
    main()