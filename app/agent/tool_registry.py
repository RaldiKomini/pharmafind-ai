from app.agent.tools import (
    run_safety_review_tool,
    render_cached_pdf_tool,
    explain_signal_tool,
    compare_drugs_tool
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_safety_review",
            "description": (
                "Run a pharmacovigilance safety review for a drug using FAERS "
                "signals and PubMed evidence. Returns structured summary data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {
                        "type": "string",
                        "description": "Drug name, e.g. Ozempic",
                    },
                    "recent_days": {
                        "type": "integer",
                        "default": 90,
                    },
                    "baseline_days": {
                        "type": "integer",
                        "default": 365,
                    },
                    "max_reports_per_window": {
                        "type": "integer",
                        "default": 1000,
                    },
                    "max_signals": {
                        "type": "integer",
                        "default": 10,
                    },
                    "max_pubmed_papers_per_signal": {
                        "type": "integer",
                        "default": 3,
                    },
                },
                "required": ["drug_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "render_cached_pdf",
            "description": (
                "Generate a PDF report from the most recent cached safety review. "
                "Use this only after a review has already been run."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_signal",
            "description": (
                "Explain why a specific reaction was flagged in the most recent "
                "cached safety review. Does not rerun FAERS or PubMed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reaction": {
                        "type": "string",
                        "description": "Reaction term to explain, e.g. suicidal ideation",
                    }
                },
                "required": ["reaction"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_drugs",
            "description": (
                "Compare flagged FAERS reporting signals and PubMed evidence for two drugs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_a": {"type": "string"},
                    "drug_b": {"type": "string"},
                    "recent_days": {"type": "integer", "default": 90},
                    "baseline_days": {"type": "integer", "default": 365},
                    "max_reports_per_window": {"type": "integer", "default": 1000},
                    "max_signals": {"type": "integer", "default": 10},
                    "max_pubmed_papers_per_signal": {"type": "integer", "default": 3},
                },
                "required": ["drug_a", "drug_b"],
                "additionalProperties": False,
            },
        },
    }
]


TOOL_FUNCTIONS = {
    "run_safety_review": run_safety_review_tool,
    "render_cached_pdf": render_cached_pdf_tool,
    "explain_signal": explain_signal_tool,
    "compare_drugs": compare_drugs_tool,
}