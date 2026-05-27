import json
import os

from openai import OpenAI

from app.agent.tool_registry import TOOLS, TOOL_FUNCTIONS
from app.agent.prompts import AGENT_SYSTEM_PROMPT

MAX_AGENT_TURNS = 4
MAX_TOOL_CALLS = 3

def run_agent(user_message):
    client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    total_call_count = 0

    for _ in range(MAX_AGENT_TURNS):
        response = client.chat.completions.create(
            model = "gpt-4.1-nano",
            messages = messages,
            tools = TOOLS,
            tool_choice = "auto",
            temperature = 0.2,
        )

        message = response.choices[0].message
        messages.append(message.model_dump())

        if not message.tool_calls:
            return message.content or ""
        
        for tool_call in message.tool_calls:
            total_call_count += 1
            if total_call_count > MAX_TOOL_CALLS:
                return (
                        "I stopped because the maximum number of tool calls was reached. "
                        "Please narrow the request."
                )
        
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)


            tool_function = TOOL_FUNCTIONS[tool_name]
            tool_result = tool_function(**tool_args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

    return "I stopped because the maximum number of agent turns was reached."
