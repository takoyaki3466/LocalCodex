from pathlib import Path
import re

from config import WORKSPACE


# ============================================================
# Limits
# ============================================================

MAX_COMMAND_LENGTH = 2000

# コマンドに含まれていたら拒否するパターン
DANGEROUS_PATTERNS = [
    # Windows filesystem deletion
    r"\bdel\b",
    r"\berase\b",
    r"\brd\b",
    r"\brmdir\b",
    r"\bRemove-Item\b",

    # Unix deletion
    r"\brm\b",

    # Disk operations
    r"\bformat\b",
    r"\bdiskpart\b",

    # Registry
    r"\breg\s+(delete|add|import|save|restore)\b",

    # System shutdown / restart
    r"\bshutdown\b",
    r"\bRestart-Computer\b",
    r"\bStop-Computer\b",

    # Process killing
    r"\btaskkill\b",
    r"\bStop-Process\b",

    # Network configuration
    r"\bnetsh\b",

    # PowerShell encoded commands
    r"-EncodedCommand\b",
    r"-enc\b",

    # PowerShell download / execution patterns
    r"\bInvoke-WebRequest\b",
    r"\bInvoke-RestMethod\b",
    r"\bStart-BitsTransfer\b",
    r"\bcertutil\b",

    # curl/wget download
    r"\bcurl\b.*\s(-o|--output)\b",
    r"\bwget\b",

    # chmod / privilege escalation
    r"\bchmod\b",
    r"\bsudo\b",

    # Environment / command execution tricks
    r"\bInvoke-Expression\b",
    r"\bIEX\b",

    # Base64 decode patterns
    r"\bFromBase64String\b",
]


# ============================================================
# Workspace path validation
# ============================================================

def is_path_inside_workspace(path: Path) -> bool:
    try:
        path.resolve().relative_to(WORKSPACE.resolve())
        return True
    except ValueError:
        return False


def extract_absolute_paths(command: str) -> list[str]:
    """
    Windows commandから明らかな絶対パスを抽出する。

    完璧なPowerShell parserではないため、
    あくまで第一段階の安全チェックとして使用する。
    """

    patterns = [
        # C:\...
        r"[A-Za-z]:\\[^\s\"']+",

        # UNC path
        r"\\\\[^\s\"']+",
    ]

    results = []

    for pattern in patterns:
        results.extend(re.findall(pattern, command))

    return results


# ============================================================
# Dangerous command detection
# ============================================================

def contains_dangerous_command(command: str) -> tuple[bool, str | None]:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, pattern

    return False, None


# ============================================================
# Command validation
# ============================================================

def validate_command(command: str) -> tuple[bool, str]:

    if not command or not command.strip():
        return False, "Empty command."

    command = command.strip()

    # --------------------------------------------------------
    # Length
    # --------------------------------------------------------

    if len(command) > MAX_COMMAND_LENGTH:
        return False, (
            f"Command is too long. "
            f"Maximum length is {MAX_COMMAND_LENGTH} characters."
        )

    # --------------------------------------------------------
    # Dangerous command
    # --------------------------------------------------------

    dangerous, pattern = contains_dangerous_command(command)

    if dangerous:
        return False, (
            f"Dangerous command detected. "
            f"Blocked pattern: {pattern}"
        )

    # --------------------------------------------------------
    # Absolute path check
    # --------------------------------------------------------

    absolute_paths = extract_absolute_paths(command)

    for raw_path in absolute_paths:

        # Ignore URLs
        if raw_path.startswith("http://"):
            continue

        if raw_path.startswith("https://"):
            continue

        try:
            path = Path(raw_path)

            if path.is_absolute() and not is_path_inside_workspace(path):
                return False, (
                    "Command contains a path outside the workspace:\n"
                    f"{raw_path}"
                )

        except Exception:
            # パス解析失敗時は安全側に倒す
            return False, (
                f"Could not safely validate path: {raw_path}"
            )

    # --------------------------------------------------------
    # Parent directory traversal
    # --------------------------------------------------------

    normalized = command.replace("\\", "/")

    # ../ や ..\ を検出
    if re.search(r"(^|[\s\"'])\.\.(?:/|\\|$)", normalized):
        return False, (
            "Parent directory traversal is not allowed."
        )

    # --------------------------------------------------------
    # Windows drive switching
    # --------------------------------------------------------

    if re.search(r"(^|[\s\"'])[" + "A-Za-z" + r"]:[/\\]", command):
        for raw_path in absolute_paths:

            try:
                path = Path(raw_path)

                if not is_path_inside_workspace(path):
                    return False, (
                        "Access to another drive/path is not allowed."
                    )

            except Exception:
                return False, (
                    f"Could not validate path: {raw_path}"
                )

    return True, "OK"