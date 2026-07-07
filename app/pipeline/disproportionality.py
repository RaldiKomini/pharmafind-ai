from dataclasses import dataclass
import math


Z_95 = 1.959963984540054


@dataclass(frozen=True)
class ContingencyTable:
    """Report-level 2x2 table for one drug and one adverse event."""

    drug_with_event: int
    drug_without_event: int
    other_drugs_with_event: int
    other_drugs_without_event: int

    def __post_init__(self) -> None:
        cells = (
            self.drug_with_event,
            self.drug_without_event,
            self.other_drugs_with_event,
            self.other_drugs_without_event,
        )
        if any(not isinstance(value, int) or value < 0 for value in cells):
            raise ValueError("Contingency-table cells must be non-negative integers")
        if self.drug_with_event + self.drug_without_event == 0:
            raise ValueError("Target-drug report total must be greater than zero")
        if self.other_drugs_with_event + self.other_drugs_without_event == 0:
            raise ValueError("Comparator report total must be greater than zero")


@dataclass(frozen=True)
class DisproportionalityMetrics:
    """PRR/ROR estimates and log-scale Wald confidence intervals."""

    prr: float
    prr_ci_low: float
    prr_ci_high: float
    ror: float
    ror_ci_low: float
    ror_ci_high: float
    continuity_corrected: bool


def _ratio_interval(estimate: float, standard_error: float) -> tuple[float, float]:
    log_estimate = math.log(estimate)
    return (
        math.exp(log_estimate - Z_95 * standard_error),
        math.exp(log_estimate + Z_95 * standard_error),
    )


def calculate_disproportionality(
    table: ContingencyTable,
) -> DisproportionalityMetrics:
    """Calculate PRR, ROR, and 95% confidence intervals.

    If any cell is zero, the Haldane-Anscombe correction adds 0.5 to all four
    cells. The result explicitly records that correction for display and audit.
    """
    raw_cells = (
        table.drug_with_event,
        table.drug_without_event,
        table.other_drugs_with_event,
        table.other_drugs_without_event,
    )
    corrected = any(value == 0 for value in raw_cells)
    correction = 0.5 if corrected else 0.0
    a, b, c, d = (value + correction for value in raw_cells)

    drug_rate = a / (a + b)
    comparator_rate = c / (c + d)
    prr = drug_rate / comparator_rate
    ror = (a * d) / (b * c)

    prr_variance = (1 / a) - (1 / (a + b)) + (1 / c) - (1 / (c + d))
    prr_se = math.sqrt(max(0.0, prr_variance))
    ror_se = math.sqrt((1 / a) + (1 / b) + (1 / c) + (1 / d))
    prr_ci_low, prr_ci_high = _ratio_interval(prr, prr_se)
    ror_ci_low, ror_ci_high = _ratio_interval(ror, ror_se)

    return DisproportionalityMetrics(
        prr=prr,
        prr_ci_low=prr_ci_low,
        prr_ci_high=prr_ci_high,
        ror=ror,
        ror_ci_low=ror_ci_low,
        ror_ci_high=ror_ci_high,
        continuity_corrected=corrected,
    )
