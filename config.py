from pathlib import Path


# ============================================================
# Workspace
# ============================================================

WORKSPACE = Path(
    r"C:\Users\takoa\Desktop\local-codex\workspace"
).resolve()

BACKUP_DIR = WORKSPACE / ".agent_backups"


# ============================================================
# LLM
# ============================================================

LLM_BASE_URL = "http://127.0.0.1:8080/v1"
LLM_API_KEY = "local"
MODEL = "local-qwen"


# ============================================================
# Agent
# ============================================================

TEMPERATURE = 0.2
MAX_TOKENS = 4096


# ============================================================
# Tool
# ============================================================

MAX_SEARCH_RESULTS = 100
MAX_SEARCH_FILE_SIZE = 10 * 1024 * 1024

MAX_CONTEXT_MESSAGES = 12
MAX_TOOL_RESULT_CHARS = 12000