from config import (
    MAX_CONTEXT_MESSAGES,
    MAX_TOOL_RESULT_CHARS,
)


def trim_tool_result(text: str) -> str:
    """
    Tool結果が巨大になりすぎないように制限する。
    """

    if text is None:
        return ""

    if len(text) <= MAX_TOOL_RESULT_CHARS:
        return text

    return (
        text[:MAX_TOOL_RESULT_CHARS]
        + "\n\n"
        + "[Tool result truncated]"
        + f"\n元の文字数: {len(text)}"
    )


def compact_messages(messages: list[dict]) -> list[dict]:
    """
    会話履歴を整理する。
    """

    if not messages:
        return messages

    system_messages = [
        message
        for message in messages
        if message.get("role") == "system"
    ]

    non_system = [
        message
        for message in messages
        if message.get("role") != "system"
    ]

    if len(non_system) > MAX_CONTEXT_MESSAGES:
        non_system = non_system[-MAX_CONTEXT_MESSAGES:]

    return system_messages + non_system


def prepare_messages(messages: list[dict]) -> list[dict]:
    """
    LLMへ送信する前にmessagesを整理する。
    """

    result = []

    for message in messages:
        message = message.copy()

        if message.get("role") == "tool":
            message["content"] = trim_tool_result(
                message.get("content", "")
            )

        result.append(message)

    return compact_messages(result)