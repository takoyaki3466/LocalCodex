from pathlib import Path
from datetime import datetime
import shutil

from config import WORKSPACE, BACKUP_DIR


# Path安全確認
def safe_path(path_str: str) -> Path:
    path = (WORKSPACE / path_str).resolve()

    try:
        path.relative_to(WORKSPACE)
    except ValueError:
        raise ValueError("Workspace外のファイルにはアクセスできません。")

    return path


# list_files
def list_files(path: str = ".") -> str:
    directory = safe_path(path)

    if not directory.exists():
        return f"ディレクトリが存在しません: {path}"

    if not directory.is_dir():
        return f"ディレクトリではありません: {path}"

    results = []

    for item in sorted(directory.iterdir()):

        if item.name == ".agent_backups":
            continue

        if item.is_dir():
            results.append(f"[DIR]{item.relative_to(WORKSPACE)}")
        else:
            results.append(f"[FILE]{item.relative_to(WORKSPACE)}")

    if not results:
        return "(空)"

    return "\n".join(results)


# read_file
def read_file(path: str) -> str:
    file_path = safe_path(path)

    if not file_path.exists():
        return f"ファイルが存在しません: {path}"

    if not file_path.is_file():
        return f"ファイルではありません: {path}"

    try:
        return file_path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return "UTF-8として読み込めませんでした。"


# backup
def backup_file(file_path: Path) -> str | None:
    if not file_path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    backup_dir = BACKUP_DIR / timestamp

    backup_dir.mkdir(parents=True, exist_ok=True)

    relative = file_path.relative_to(WORKSPACE)

    backup_path = backup_dir / relative

    backup_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(file_path, backup_path)

    return str(backup_path.relative_to(WORKSPACE))


# write_file
def write_file(path: str, content: str) -> str:
    file_path = safe_path(path)

    old_exists = file_path.exists()

    print()
    print("=" * 60)
    print(" ファイル変更確認")
    print("=" * 60)

    if old_exists:
        print("操作 : 既存ファイルを上書き")
    else:
        print("操作 : 新規ファイル作成")

    print(f"ファイル : {path}")
    print()
    print("--- 新しい内容 ---")

    preview = content

    if len(preview) > 5000:
        preview = (preview[:5000] + "\n... (省略)")

    print(preview)

    print()

    answer = input("この変更を適用しますか？ [y/N] > ")

    if answer.lower() != "y":
        return "ユーザーによって""変更がキャンセルされました。"

    backup = backup_file(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")

    if backup:
        return "ファイルを書き込みました。"f"バックアップ: {backup}"

    return "ファイルを書き込みました。"


# edit_file
def edit_file(path: str, old_text: str, new_text: str) -> str:
    file_path = safe_path(path)

    if not file_path.exists():
        return f"ファイルが存在しません: {path}"

    try:
        content = file_path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return "UTF-8として読み込めませんでした。"

    count = content.count(old_text)

    if count == 0:
        return "指定された変更対象の文字列が見つかりませんでした。"

    if count > 1:
        return f"変更対象の文字列が{count}箇所あります。意図しない複数箇所の変更を防ぐため中止しました。"

    new_content = content.replace(old_text, new_text, 1)

    print()
    print("=" * 60)
    print(" ファイル変更確認")
    print("=" * 60)
    print("操作 : ファイルの部分編集")
    print(f"ファイル : {path}")
    print()

    print("--- 変更前 ---")
    print(old_text)

    print()
    print("--- 変更後 ---")
    print(new_text)

    print()

    answer = input("この変更を適用しますか？ [y/N] > ")

    if answer.lower() != "y":
        return "ユーザーによって変更がキャンセルされました。"

    backup = backup_file(file_path)

    file_path.write_text(new_content, encoding="utf-8")

    return "ファイルを編集しました。"f"バックアップ: {backup}"
