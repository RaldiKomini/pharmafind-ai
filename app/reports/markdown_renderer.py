from app.pipeline.review_summary import ReviewSummary


def render_markdown_report(summary: ReviewSummary) -> str:
    """
    Render a deterministic Markdown safety-review brief.

    This report does not provide medical advice or claim causality.
    """

    lines: list[str] = []

    lines.append(f"# Safety Review Brief: {summary.drug_name}")
    lines.append("")

    lines.append("## Important Disclaimer")
    lines.append(
        "This report is not medical advice. FAERS reports are spontaneous adverse event reports "
        "and do not establish causality. Flagged patterns should be interpreted only as signals "
        "for human pharmacovigilance review."
    )
    lines.append("")

    lines.append("## Data Windows")
    lines.append(f"- Recent window: {summary.recent_start} to {summary.recent_end}")
    lines.append(f"- Baseline window: {summary.baseline_start} to {summary.baseline_end}")
    lines.append("")

    lines.append("## Report Counts")
    lines.append(f"- Recent FAERS reports: {summary.recent_report_count}")
    lines.append(f"- Baseline FAERS reports: {summary.baseline_report_count}")
    lines.append("")

    lines.append("## Flagged Reporting Signals")
    lines.append("")
    lines.append(
        "| Reaction | Recent Count | Baseline Count | Ratio | Score | PubMed Evidence |"
    )
    lines.append(
        "|---|---:|---:|---:|---:|---|"
    )

    if not summary.signals:
        lines.append("| No flagged signals found | - | - | - | - | - |")
    else:
        for signal in summary.signals:
            lines.append(
                f"| {signal.reaction} "
                f"| {signal.recent_count} "
                f"| {signal.baseline_count} "
                f"| {signal.ratio:.2f} "
                f"| {signal.signal_score:.2f} "
                f"| {signal.evidence.evidence_grade} "
                f"|"
            )

    lines.append("")
    lines.append("## Literature Evidence")
    lines.append("")

    if not summary.signals:
        lines.append("No PubMed evidence was searched because no reporting signals were flagged.")
    else:
        for signal in summary.signals:
            lines.append(f"### {signal.reaction}")
            lines.append(f"- Evidence grade: {signal.evidence.evidence_grade}")
            lines.append(f"- PubMed papers found: {signal.evidence.paper_count}")
            lines.append("")

            if signal.evidence.papers:
                for paper in signal.evidence.papers:
                    lines.append(
                        f"- {paper.title} "
                        f"({paper.pub_date or 'unknown date'}) "
                        f"[PMID: {paper.pmid}]"
                    )
            else:
                lines.append("- No PubMed papers found for this drug/reaction query.")

            lines.append("")

    lines.append("## Limitations")
    lines.append("")

    for limitation in summary.limitations:
        lines.append(f"- {limitation}")

    lines.append("")

    return "\n".join(lines)