from dataclasses import dataclass

@dataclass(frozen=True)
class SignalDetectionConfig:
    """Thresholds used to keep the signal table focused and less noisy."""

    min_recent_count: int = 10
    min_baseline_count: int = 3
    min_ratio: float = 2.0
    max_signals: int = 20


def detect_signals(comparisons, config):

    """
    Filter reaction comparisons into potential safety signals.

    These are not causal claims.
    They are reporting-pattern signals for human review.
    """
        
    if config is None:
        config = SignalDetectionConfig()

    signals = []
    for item in comparisons:

        if item.recent_count < config.min_recent_count:
            continue
        if item.baseline_count < config.min_baseline_count:
            continue
        if item.ratio < config.min_ratio:
            continue
        signals.append(item)
        if len(signals)  == config.max_signals:
            break

    return signals

