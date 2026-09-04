import re

from config import (
    WORKSPACE,
    MAX_SEARCH_RESULTS,
    MAX_SEARCH_FILE_SIZE,
)

from tools.filesystem import safe_path


EXCLUDED_DIRS = {
    ".git",
    ".gradle",
    "build",
    "out",
    "node_modules",
    ".idea",
    ".vscode",
    ".agent_backups",
    "__pycache__",
}


EXCLUDED_EXTENSIONS = {
    ".class",
    ".jar",
    ".zip",
    ".7z",
    ".rar",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".ico",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".dat",
}


def grep_search(
    query: str,
    path: str = ".",
    case_sensitive: bool = False,
    use_regex: bool = False,
    context_lines: int = 2,
    max_results: int = MAX_SEARCH_RESULTS,
) -> str:

    root = safe_path(path)

    if not root.exists():
        return f"検索対象が存在しません: {path}"

    if not query:
        return "検索文字列が空です。"

    context_lines = max(
        0,
        min(context_lines, 10)
    )

    max_results = max(
        1,
        min(max_results, 500)
    )

    # --------------------------------------------------------
    # 正規表現
    # --------------------------------------------------------

    if use_regex:

        flags = (
            0
            if case_sensitive
            else re.IGNORECASE
        )

        try:
            pattern = re.compile(
                query,
                flags
            )

        except re.error as e:
            return (
                f"正規表現が不正です: {e}"
            )

    # --------------------------------------------------------
    # ファイル取得
    # --------------------------------------------------------

    if root.is_file():

        files = [root]

    else:

        files = []

        for file_path in root.rglob("*"):

            if not file_path.is_file():
                continue

            if any(
                part in EXCLUDED_DIRS
                for part in file_path.parts
            ):
                continue

            if (
                file_path.suffix.lower()
                in EXCLUDED_EXTENSIONS
            ):
                continue

            files.append(file_path)

    results = []
    match_count = 0

    # --------------------------------------------------------
    # 検索
    # --------------------------------------------------------

    for file_path in files:

        try:
            if (
                file_path.stat().st_size
                > MAX_SEARCH_FILE_SIZE
            ):
                continue

        except OSError:
            continue

        try:

            lines = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            ).splitlines()

        except Exception:
            continue

        for index, line in enumerate(lines):

            if use_regex:

                matched = (
                    pattern.search(line)
                    is not None
                )

            elif case_sensitive:

                matched = query in line

            else:

                matched = (
                    query.lower()
                    in line.lower()
                )

            if not matched:
                continue

            match_count += 1

            relative = (
                file_path.relative_to(
                    WORKSPACE
                )
            )

            start = max(
                0,
                index - context_lines
            )

            end = min(
                len(lines),
                index + context_lines + 1
            )

            results.append(
                f"\n--- {relative}:{index + 1} ---"
            )

            for line_index in range(
                start,
                end
            ):

                prefix = (
                    ">"
                    if line_index == index
                    else " "
                )

                results.append(
                    f"{prefix} "
                    f"{line_index + 1:5}: "
                    f"{lines[line_index]}"
                )

            if match_count >= max_results:

                results.append(
                    "\n検索結果が多いため、"
                    f"最大{max_results}件で停止しました。"
                )

                return "\n".join(results)

    if not results:

        return (
            f"「{query}」は見つかりませんでした。"
        )

    results.insert(
        0,
        f"検索結果: {match_count}件"
    )

    return "\n".join(results)