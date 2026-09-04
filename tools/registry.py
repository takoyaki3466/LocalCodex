from tools.filesystem import (
    list_files,
    read_file,
    write_file,
    edit_file,
)

from tools.search import grep_search

from tools.shell import exec_shell_command


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path inside the workspace."
                    }
                },
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path."
                    }
                },
                "required": ["path"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search text inside workspace files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text or regex to search for."
                    },
                    "context_lines": {
                        "type": "integer",
                        "description": "Number of context lines."
                    },
                },
                "required": ["query"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or completely replace a file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                    },
                    "content": {
                        "type": "string",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace an exact piece of text inside a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                    },
                    "old_text": {
                        "type": "string",
                    },
                    "new_text": {
                        "type": "string",
                    },
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "exec_shell_command",
            "description": (
                "Execute a shell command inside the workspace. "
                "Use this for builds, tests, Gradle commands, "
                "Git commands, and other development tasks. "
                "The user must approve execution."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute."
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds.",
                        "default": 120,
                    },
                },
                "required": ["command"],
            },
        },
    },
]


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "grep_search": grep_search,
    "write_file": write_file,
    "edit_file": edit_file,
    "exec_shell_command": exec_shell_command,
}


def execute_tool(name, arguments):
    function = TOOL_FUNCTIONS.get(name)

    if function is None:
        return f"Unknown tool: {name}"

    try:
        return function(**arguments)

    except Exception as e:
        return f"Tool execution error: {type(e).__name__}: {e}"