# Example Outputs

These files show the current PharmaFind AI deterministic and agent workflows.

## Deterministic review dashboard

![Deterministic PRR/ROR review](screenshots/deterministic-review.png)

This screenshot shows:

- configurable analysis settings;
- PRR/ROR signal table with 95% confidence intervals;
- PubMed retrieval counts;
- grounded literature stance badges;
- PDF export from the displayed Markdown report.

## Agent workflow

![Agent workflow](screenshots/agent-workflow.png)

This screenshot shows the agent answering a multi-step comparison prompt by using the same deterministic backend tools as the dashboard.

## Sample PDF

- [Ozempic safety review PDF](example-output/ozempic_safety_review.pdf)

The sample PDF is generated with ReportLab from the Markdown safety brief. It does not require WeasyPrint or native Pango/Cairo dependencies.
