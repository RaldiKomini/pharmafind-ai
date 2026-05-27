import json
import os

from openai import OpenAI

from app.pipeline.review_summary import ReviewSummary, review_summary_to_dict
from app.llm.prompts import SAFETY_BRIEF_SYSTEM_PROMPT


def generate_llm_safety_brief(summary: ReviewSummary):
    """
    Generate a polished Markdown safety-review brief from a compact ReviewSummary.

    The LLM receives only structured summary data, not raw FAERS reports.
    """
    client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
    summary_dict = review_summary_to_dict(summary)

    response = client.chat.completions.create(
        model = "gpt-4.1-mini",
        temperature = 0.2,
        messages = [
            {
                "role":"system",
                "content": SAFETY_BRIEF_SYSTEM_PROMPT,

            },
            {
                "role":"user",
                "content": (
                    "Write a structured Markdown pharmacovigilance safety-review brief from this compact summary \n\n"
                    f"{json.dumps(summary_dict, indent = 2)}"
                ),
            },
        ],
    )

    return response.choices[0].message.content

