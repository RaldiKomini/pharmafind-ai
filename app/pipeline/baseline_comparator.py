from dataclasses import dataclass
import math


@dataclass(frozen = True)
class ReactionComparison:
    """Recent-vs-baseline comparison for one normalized reaction term."""

    reaction: str
    recent_count:int
    baseline_count: int
    recent_rate: int
    baseline_rate: int
    ratio: float
    signal_score: float


def compute_signal_score(
    recent_count: int,
    ratio: float,
) -> float:
    """
    Compute a simple ranking score for potential signals.

    Uses log scaling so very common reactions do not dominate too much.
    """
    if ratio == float("inf"):
        return 0.0

    if ratio <= 1:
        return 0.0

    return math.log1p(recent_count) * ratio


def compare_reaction_counts(recent_counts, baseline_counts, total_recent_reports, total_baseline_reports):
    """
    Compare reaction reporting rates between recent and baseline windows.

    Rate means:
        reaction_count / total_reports_in_window
    """

    comparisons = []

    all_reactions = set(recent_counts) | set(baseline_counts)

    for reaction in all_reactions:
        recent_count = recent_counts.get(reaction, 0)
        baseline_count = baseline_counts.get(reaction, 0)

        if recent_count == 0:
            recent_rate = 0.0
        else:
            recent_rate = recent_count/total_recent_reports

        if baseline_count == 0:
            baseline_rate = 0.0
        else:
            baseline_rate = baseline_count / total_baseline_reports


        if baseline_rate == 0.0:
            # Keep the math explicit here; the detector later filters out
            # baseline-zero signals so infinite ratios do not dominate output.
            ratio = float("inf") if recent_rate > 0.0 else 0.0
        else:
            ratio = recent_rate / baseline_rate

        signal_score = compute_signal_score(recent_count=recent_count, ratio=ratio)

        comparisons.append(ReactionComparison(reaction, recent_count, baseline_count, recent_rate, baseline_rate, ratio, signal_score))

    return sorted(comparisons, key = lambda item:item.signal_score, reverse=True)
