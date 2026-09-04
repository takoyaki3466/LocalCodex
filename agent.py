import json

from llm import chat
from prompts import SYSTEM_PROMPT
from tools.registry import TOOLS, execute_tool
from tools.filesystem import list_files, read_file


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def run_agent(user_input: str):

    messages.append({
        "role": "user",
        "content": user_input
    })

    while True:

        message = chat(messages, tools=TOOLS)

        # 通常の回答
        if not message.tool_calls:

            print()
            print("Agent >")
            print(message.content)

            messages.append({"role": "assistant", "content": message.content})
            break

        # Tool Call
        messages.append({"role": "assistant", "content": message.content, "tool_calls": [{
                    "id": tool_call.id, "type": "function",
                 "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]
        })

        for tool_call in message.tool_calls:

            name = tool_call.function.name

            try:

                arguments = json.loads(
                    tool_call.function.arguments
                )

            except json.JSONDecodeError:

                result = (
                    "Tool引数のJSON解析に失敗しました。"
                )

            else:

                print()
                print(
                    f"[Tool] {name}({arguments})"
                )

                result = execute_tool(
                    name,
                    arguments
                )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })


def clear_history():

    global messages

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


def main():

    print("=" * 60)
    print(" Local Codex Agent")
    print("=" * 60)

    from config import WORKSPACE

    print(f"Workspace: {WORKSPACE}")
    print()

    print("コマンド:")
    print("  /files   - ファイル一覧")
    print("  /read    - ファイル読み込み")
    print("  /clear   - 会話履歴を消去")
    print("  /exit    - 終了")
    print()

    while True:

        try:

            user_input = input(
                "You > "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError
        ):

            print()
            break

        if not user_input:
            continue

        if user_input == "/exit":
            break

        if user_input == "/clear":

            clear_history()

            print(
                "会話履歴を消去しました。"
            )

            continue

        if user_input == "/files":

            print()
            print(list_files())

            continue

        if user_input.startswith("/read "):

            path = user_input[6:].strip()

            print()
            print(read_file(path))

            continue

        run_agent(user_input)


if __name__ == "__main__":
    main()