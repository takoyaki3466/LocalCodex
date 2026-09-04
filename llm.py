from openai import OpenAI

from config import (
    LLM_BASE_URL,
    LLM_API_KEY,
    MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

from context import prepare_messages


client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
)


def chat(messages, tools=None):

    messages = prepare_messages(messages)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    return response.choices[0].message