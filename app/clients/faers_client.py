from dataclasses import dataclass
from datetime import date, datetime
import os
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


OPENFDA_FAERS_URL = "https://api.fda.gov/drug/event.json"
OPENFDA_MAX_UNAUTHENTICATED_LIMIT = 100
OPENFDA_MAX_COUNT_TERMS = 1000


@dataclass(frozen=True)
class FaersQueryConfig:
    """Parameters for one raw-report openFDA query.

    Raw fetching remains available for the smoke scripts. The production signal
    pipeline uses aggregate count queries instead of capped report samples.
    """

    drug_name: str
    limit: int = 100
    start_date: date | None = None
    end_date: date | None = None
    sort: str | None = "receivedate:desc"


@dataclass(frozen=True)
class FaersTermCount:
    """One term and its report count from an openFDA count aggregation."""

    term: str
    count: int


def format_faers_date(value: date) -> str:
    """Convert a Python date to the YYYYMMDD format expected by openFDA."""
    return value.strftime("%Y%m%d")


def escape_openfda_exact_value(value: str) -> str:
    """Escape a user value before placing it in a quoted openFDA expression."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_date_search(start_date: date, end_date: date) -> str:
    """Build an inclusive received-date search expression."""
    return (
        f"receivedate:[{format_faers_date(start_date)} "
        f"TO {format_faers_date(end_date)}]"
    )


def build_drug_search(drug_name: str) -> str:
    """Match reported, harmonized brand/generic, and active-substance names.

    The event API cannot reliably bind a separate drug-role condition to this
    exact drug object, so this deliberately represents all mentions of the drug.
    """
    normalized = escape_openfda_exact_value(drug_name.strip().upper())
    fields = (
        "patient.drug.medicinalproduct.exact",
        "patient.drug.openfda.brand_name.exact",
        "patient.drug.openfda.generic_name.exact",
        "patient.drug.activesubstance.activesubstancename.exact",
    )
    return "(" + " OR ".join(f'{field}:"{normalized}"' for field in fields) + ")"


def build_reaction_search(reaction: str) -> str:
    """Build an exact MedDRA preferred-term search expression."""
    normalized = escape_openfda_exact_value(reaction.strip().upper())
    return f'patient.reaction.reactionmeddrapt.exact:"{normalized}"'


def _retrying_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


class FaersClient:
    """Client for raw and aggregate openFDA FAERS queries."""

    def __init__(
        self,
        base_url: str = OPENFDA_FAERS_URL,
        timeout: int = 30,
        session: requests.Session | None = None,
        api_key: str | None = None,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.session = session or _retrying_session()
        self.api_key = api_key or os.getenv("OPENFDA_API_KEY")
        self.max_count_terms = (
            OPENFDA_MAX_COUNT_TERMS
            if self.api_key
            else OPENFDA_MAX_UNAUTHENTICATED_LIMIT
        )
        self._report_count_cache: dict[str, int] = {}
        self._term_count_cache: dict[tuple[str, str, int], list[FaersTermCount]] = {}

    def _get_json(self, params: dict[str, Any]) -> dict[str, Any]:
        if self.api_key:
            params = {**params, "api_key": self.api_key}
        response = self.session.get(
            self.base_url,
            params=params,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return {"meta": {"results": {"total": 0}}, "results": []}
        response.raise_for_status()
        return response.json()

    def count_reports(self, search: str) -> int:
        """Return the complete number of reports matching a search expression."""
        if search in self._report_count_cache:
            return self._report_count_cache[search]

        data = self._get_json({"search": search, "limit": 1})
        total = int(data.get("meta", {}).get("results", {}).get("total", 0))
        self._report_count_cache[search] = total
        return total

    def count_terms(
        self,
        search: str,
        field: str,
        limit: int = OPENFDA_MAX_COUNT_TERMS,
    ) -> list[FaersTermCount]:
        """Return report-level term counts inside the matching report set."""
        bounded_limit = max(1, min(limit, self.max_count_terms))
        cache_key = (search, field, bounded_limit)
        if cache_key in self._term_count_cache:
            return self._term_count_cache[cache_key]

        data = self._get_json(
            {"search": search, "count": field, "limit": bounded_limit}
        )
        counts = [
            FaersTermCount(term=str(item["term"]), count=int(item["count"]))
            for item in data.get("results", [])
            if item.get("term") and int(item.get("count", 0)) >= 0
        ]
        self._term_count_cache[cache_key] = counts
        return counts

    def fetch_latest_received_date(self) -> date:
        """Return the latest receivedate currently available from openFDA."""
        data = self._get_json({"sort": "receivedate:desc", "limit": 1})
        results = data.get("results", [])
        if not results or not results[0].get("receivedate"):
            raise RuntimeError("openFDA did not return a latest FAERS receivedate")
        return datetime.strptime(results[0]["receivedate"], "%Y%m%d").date()

    def resolve_drug_aliases(self, drug_name: str, limit: int = 10) -> list[str]:
        """Resolve literature-search aliases from matching drug objects.

        Search predicates can match different items in an array, so aliases are
        collected only after locally confirming the input and alias fields belong
        to the same patient.drug object.
        """
        normalized_input = drug_name.strip().upper()
        aliases: list[str] = [drug_name.strip()]
        data = self._get_json(
            {
                "search": build_drug_search(drug_name),
                "limit": max(1, min(limit, OPENFDA_MAX_UNAUTHENTICATED_LIMIT)),
                "sort": "receivedate:desc",
            }
        )

        for report in data.get("results", []):
            for drug in report.get("patient", {}).get("drug", []):
                openfda = drug.get("openfda", {})
                candidate_values: list[str] = []
                medicinal_product = drug.get("medicinalproduct")
                if isinstance(medicinal_product, str):
                    candidate_values.append(medicinal_product)
                active_name = drug.get("activesubstance", {}).get("activesubstancename")
                if isinstance(active_name, str):
                    candidate_values.append(active_name)
                for field in ("brand_name", "generic_name", "substance_name"):
                    values = openfda.get(field, [])
                    if isinstance(values, str):
                        values = [values]
                    candidate_values.extend(value for value in values if isinstance(value, str))

                if not any(value.strip().upper() == normalized_input for value in candidate_values):
                    continue
                for value in candidate_values:
                    cleaned = value.strip()
                    if cleaned and cleaned.upper() not in {item.upper() for item in aliases}:
                        aliases.append(cleaned)

        return aliases[:12]

    def fetch_reports(self, config: FaersQueryConfig) -> list[dict[str, Any]]:
        """Fetch raw reports for legacy smoke scripts and targeted inspection."""
        reports: list[dict[str, Any]] = []
        search_parts = [
            f'patient.drug.medicinalproduct:"{escape_openfda_exact_value(config.drug_name)}"'
        ]

        if config.start_date is not None and config.end_date is not None:
            search_parts.append(build_date_search(config.start_date, config.end_date))

        search = " AND ".join(search_parts)
        while len(reports) < config.limit:
            page_limit = min(
                OPENFDA_MAX_UNAUTHENTICATED_LIMIT,
                config.limit - len(reports),
            )
            params: dict[str, Any] = {
                "search": search,
                "limit": page_limit,
                "skip": len(reports),
            }
            if config.sort:
                params["sort"] = config.sort

            data = self._get_json(params)
            page_results = data.get("results", [])
            if not page_results:
                break

            reports.extend(page_results)
            if len(page_results) < page_limit:
                break

        return reports
