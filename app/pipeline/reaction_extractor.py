from collections.abc import Iterable

def extract_reaction_terms(report: dict):
    """
    Extract MedDRA preferred reaction terms from a single FAERS report.

    Returns lowercase normalized terms.
    """

    reactions = report.get("patient", {}).get("reaction", [])
    
    terms: list[str] = []
    for reaction in reactions:
        term = reaction.get("reactionmeddrapt")

        if isinstance(term, str) and term.strip():
            terms.append(term.strip().lower())

    return terms



def extract_all_reaction_terms(reports: Iterable[dict]):
    """
    Extract reaction terms from multiple FAERS reports.
    """
    all_terms = []

    for report in reports:
        all_terms.extend(extract_reaction_terms(report))
    return all_terms
