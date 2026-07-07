# Architecture

![PharmaFind AI system architecture](architecture.png)

Printable version: [architecture.pdf](architecture.pdf)

## Main Flow

1. The user can start from either the deterministic review dashboard or the agentic chat workflow.
2. Both paths call the same typed FastAPI backend.
3. The backend review toolset runs the deterministic FAERS pipeline.
4. openFDA aggregate counts produce the 2x2 drug/event tables.
5. The backend calculates PRR, ROR, confidence intervals, and threshold decisions.
6. Flagged signals enter the PubMed RAG path, where ESearch and EFetch retrieve candidate abstracts.
7. Optional embeddings rerank the retrieved RAG context.
8. Optional structured LLM synthesis summarizes only retrieved abstracts.
9. PMID validation rejects citations outside the retrieved set.
10. The app renders dashboard artifacts, agentic answers, Markdown, and ReportLab PDF output.

## Agent Flow

Agent mode sits beside the deterministic dashboard as a first-class workflow. It can call backend tools for review, comparison, explanation, and PDF rendering. The agent uses session cache state for follow-up requests, but the deterministic pipeline remains the source of truth for statistics and citations.

## Safety Boundaries

- Signals are for qualified human review only.
- FAERS reports do not establish causality.
- PRR and ROR are reporting-disproportionality measures, not incidence rates.
- The LLM cannot add papers; every cited PMID must come from the retrieved PubMed set.
