from dataclasses import dataclass
from typing import Any
import requests
from datetime import date

OPENFDA_FAERS_URL = "https://api.fda.gov/drug/event.json"
OPENFDA_MAX_UNAUTHENTICATED_LIMIT = 100

@dataclass(frozen = True)
class FaersQueryConfig:
    """Parameters for one openFDA FAERS query window."""

    drug_name: str
    limit: int = 100
    start_date: date | None = None
    end_date: date | None = None
    sort: str | None = "receivedate:desc"


def format_faers_date(value: date) -> str:
    """Convert a Python date to the YYYYMMDD format expected by FAERS."""
    return value.strftime("%Y%m%d")


class FaersClient:
    """
    Small client for querying FDA FAERS adverse event reports through openFDA.

    This client only fetches raw reports.
    It does not aggregate, interpret, or detect safety signals.
    """

    def __init__(self, base_url: str = OPENFDA_FAERS_URL, timeout :int = 20):
        self.base_url = base_url
        self.timeout = timeout



    def fetch_reports(self, config: FaersQueryConfig) -> list[dict[str, Any]]:
        """
        Fetch FAERS reports for a drug name.

        Parameters
        ----------
        config:
            Query configuration containing the drug name and result limit.

        Returns
        -------
        list[dict[str, Any]]
            Raw FAERS report dictionaries.
        """

        reports: list[dict[str, Any]] = []
        search_parts = [
            f'patient.drug.medicinalproduct:"{config.drug_name}"'
        ]

        if config.start_date is not None and config.end_date is not None:
            start = format_faers_date(config.start_date)
            end = format_faers_date(config.end_date)
            search_parts.append(f"receivedate:[{start} TO {end}]")

        search = " AND ".join(search_parts)

        while len(reports) < config.limit:
            # openFDA caps unauthenticated requests at 100 rows, so larger
            # windows are fetched one page at a time.
            page_limit = min(
                OPENFDA_MAX_UNAUTHENTICATED_LIMIT,
                config.limit - len(reports),
            )
            params = {
                "search": search,
                "limit": page_limit,
                "skip": len(reports),
            }
            if config.sort:
                params["sort"] = config.sort

            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
            )

            if response.status_code == 404:
                break

            response.raise_for_status()
            page_results = response.json().get("results", [])
            if not page_results:
                break

            reports.extend(page_results)
            if len(page_results) < page_limit:
                break

        return reports
