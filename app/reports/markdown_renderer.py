from app.pipeline.review_summary import ReviewSummary


def _safe_table_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _pmid_link(pmid: str) -> str:
    return f"[PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)"


def render_markdown_report(summary: ReviewSummary) -> str:
    """Render reproducible statistics and PMID-grounded literature evidence."""
    lines: list[str] = [
        f"# Safety Review Brief: {summary.drug_name}",
        "",
        "## Important Disclaimer",
        "This report is not medical advice. FAERS disproportionality identifies reporting patterns, not incidence, patient risk, or causality.",
        "",
        "## Analysis Window",
        f"- Analysis period: {summary.analysis_start} to {summary.analysis_end}",
        f"- All FAERS reports in period: {summary.total_report_count:,}",
        f"- Reports mentioning {summary.drug_name}: {summary.drug_report_count:,}",
        "- Drug-role scope: all mentions (not primary-suspect-only)",
        f"- PubMed drug terms: {', '.join(summary.pubmed_search_terms)}",
        "",
        "## Flagged Reporting Signals",
        "",
        "| Reaction | Cases | PRR (95% CI) | ROR (95% CI) | Retrieved / PubMed hits |",
        "|---|---:|---:|---:|---:|",
    ]

    if not summary.signals:
        lines.append("| No signals passed the configured thresholds | - | - | - | - |")
    else:
        for signal in summary.signals:
            lines.append(
                f"| {_safe_table_text(signal.reaction)} "
                f"| {signal.case_count:,} "
                f"| {signal.prr:.2f} ({signal.prr_ci_low:.2f}–{signal.prr_ci_high:.2f}) "
                f"| {signal.ror:.2f} ({signal.ror_ci_low:.2f}–{signal.ror_ci_high:.2f}) "
                f"| {signal.evidence.retrieved_paper_count} / {signal.evidence.total_result_count} |"
            )

    lines.extend(["", "## Signal Details", ""])
    for signal in summary.signals:
        table = signal.contingency_table
        lines.extend(
            [
                f"### {signal.reaction}",
                f"- Drug + event reports: {table.drug_with_event:,}",
                f"- Drug + other-event reports: {table.drug_without_event:,}",
                f"- Other-drug + event reports: {table.other_drugs_with_event:,}",
                f"- Other-drug + other-event reports: {table.other_drugs_without_event:,}",
                f"- PRR: {signal.prr:.2f} (95% CI {signal.prr_ci_low:.2f}–{signal.prr_ci_high:.2f})",
                f"- ROR: {signal.ror:.2f} (95% CI {signal.ror_ci_low:.2f}–{signal.ror_ci_high:.2f})",
            ]
        )
        if signal.continuity_corrected:
            lines.append("- A 0.5 continuity correction was applied because at least one table cell was zero.")
        lines.append("- Threshold evaluation:")
        lines.extend(f"  - {reason}" for reason in signal.threshold_reasons)
        lines.append("")

        evidence = signal.evidence
        lines.append("#### Retrieved PubMed Evidence")
        lines.append(f"- Total PubMed matches: {evidence.total_result_count}")
        lines.append(f"- Abstracts displayed: {evidence.retrieved_paper_count}")
        lines.append(f"- Ranking method: {evidence.ranking_method}")
        lines.append(f"- Synthesis status: {evidence.synthesis_status}")
        lines.append("")

        if evidence.synthesis:
            synthesis = evidence.synthesis
            summary_pmids = sorted(
                {pmid for claim in synthesis.claims for pmid in claim.pmids}
            )
            summary_citations = ", ".join(_pmid_link(pmid) for pmid in summary_pmids)
            lines.extend(
                [
                    f"**Grounded summary ({synthesis.overall_stance}):** {synthesis.summary} ({summary_citations})",
                    "",
                ]
            )
            for claim in synthesis.claims:
                citations = ", ".join(_pmid_link(pmid) for pmid in claim.pmids)
                lines.append(f"- **{claim.stance}:** {claim.text} ({citations})")
            if synthesis.limitations:
                lines.append("")
                lines.append("Evidence limitations:")
                lines.extend(f"- {item}" for item in synthesis.limitations)
            lines.append("")

        if evidence.papers:
            for paper in evidence.papers:
                metadata = "; ".join(
                    part for part in (paper.source, paper.pub_date, paper.doi) if part
                )
                lines.append(
                    f"- **{paper.title or 'Untitled paper'}**"
                    f"{f' ({metadata})' if metadata else ''} — {_pmid_link(paper.pmid)}"
                )
                if paper.abstract:
                    lines.append(f"  - Abstract: {paper.abstract}")
        else:
            lines.append("- No PubMed abstracts were returned for this drug/event query.")
        lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in summary.limitations)
    lines.append("")
    return "\n".join(lines)
