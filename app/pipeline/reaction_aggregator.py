from collections.abc import Iterable
from collections import Counter

def aggregate_reactions(all_terms:Iterable[str], top_k: int | None = None):
    """
    Count reaction terms and optionally return only the top_k most common.
    """
    counts = Counter(all_terms)

    if top_k is None:
        return counts.most_common()
    

    return counts.most_common(top_k)


def count_reactions(reaction_terms: Iterable[str]) -> dict[str, int]:
    """
    Count reaction terms and return a plain dictionary.
    """
    return dict(Counter(reaction_terms))
