from app.agent.tools import (
    compare_drugs_tool,
    explain_signal_tool,
    render_cached_pdf_tool,
    run_safety_review_tool,
)


REVIEW_PROPERTIES = {
    "analysis_days": {"type": "integer", "default": 365},
    "min_case_count": {"type": "integer", "default": 5},
    "min_prr": {"type": "number", "default": 2.0},
    "min_ror_ci_lower": {"type": "number", "default": 1.0},
    "max_signals": {"type": "integer", "default": 10},
    "pubmed_candidate_count": {"type": "integer", "default": 25},
    "max_pubmed_papers_per_signal": {"type": "integer", "default": 5},
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_safety_review",
            "description": (
                "Run a PRR/ROR pharmacovigilance review using complete-window openFDA counts "
                "and relevance-ranked PubMed abstracts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "Brand or generic drug name"},
                    **REVIEW_PROPERTIES,
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
            "description": "Generate a PDF from the most recent cached review.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_signal",
            "description": "Return the cached PRR/ROR calculations and PubMed evidence for a reaction.",
            "parameters": {
                "type": "object",
                "properties": {"reaction": {"type": "string"}},
                "required": ["reaction"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_drugs",
            "description": "Compare independently calculated reporting signals for two drugs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_a": {"type": "string"},
                    "drug_b": {"type": "string"},
                    **REVIEW_PROPERTIES,
                },
                "required": ["drug_a", "drug_b"],
                "additionalProperties": False,
            },
        },
    },
]


TOOL_FUNCTIONS = {
    "run_safety_review": run_safety_review_tool,
    "render_cached_pdf": render_cached_pdf_tool,
    "explain_signal": explain_signal_tool,
    "compare_drugs": compare_drugs_tool,
}
