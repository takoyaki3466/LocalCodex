import subprocess

from config import WORKSPACE
from tools.safety import validate_command


# ============================================================
# Limits
# ============================================================

DEFAULT_TIMEOUT = 120
MAX_TIMEOUT = 300

MAX_OUTPUT_LENGTH = 30000


# ============================================================
# Shell execution
# ============================================================

def exec_shell_command(
    command: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:

    # --------------------------------------------------------
    # Validate timeout
    # --------------------------------------------------------

    try:
        timeout = int(timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT

    timeout = max(1, min(timeout, MAX_TIMEOUT))

    # --------------------------------------------------------
    # Validate command
    # --------------------------------------------------------

    valid, reason = validate_command(command)

    if not valid:
        return (
            "Command rejected by safety policy.\n"
            f"Reason: {reason}"
        )

    # --------------------------------------------------------
    # User confirmation
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Shell command requested:")
    print(command)
    print("=" * 60)
    print(f"Working directory: {WORKSPACE}")
    print(f"Timeout: {timeout}s")
    print()

    answer = input(
        "Execute this command? [y/N]: "
    ).strip().lower()

    if answer not in ("y", "yes"):
        return "Command execution cancelled by user."

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            command,
            cwd=WORKSPACE,
            shell=True,

            capture_output=True,
            text=True,

            encoding="utf-8",
            errors="replace",

            timeout=timeout,
        )

        stdout = result.stdout or ""
        stderr = result.stderr or ""

        # ----------------------------------------------------
        # Limit output
        # ----------------------------------------------------

        if len(stdout) > MAX_OUTPUT_LENGTH:
            stdout = (
                stdout[:MAX_OUTPUT_LENGTH]
                + "\n\n[STDOUT TRUNCATED]"
            )

        if len(stderr) > MAX_OUTPUT_LENGTH:
            stderr = (
                stderr[:MAX_OUTPUT_LENGTH]
                + "\n\n[STDERR TRUNCATED]"
            )

        # ----------------------------------------------------
        # Build result
        # ----------------------------------------------------

        output = []

        output.append(
            f"Exit code: {result.returncode}"
        )

        if stdout:
            output.append("")
            output.append("STDOUT:")
            output.append(stdout)

        if stderr:
            output.append("")
            output.append("STDERR:")
            output.append(stderr)

        return "\n".join(output)

    except subprocess.TimeoutExpired:

        return (
            f"Command timed out after {timeout} seconds."
        )

    except Exception as e:

        return (
            "Command execution failed.\n"
            f"{type(e).__name__}: {e}"
        )