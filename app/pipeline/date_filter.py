from datetime import date, datetime, timedelta
from typing import Any


def parse_faers_date(value :str) -> date | None:
    """
    FAERS dates usually look like: YYYYMMDD, e.g. 20250131.
    """

    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        return None
    
    
def get_report_received_date(report: dict[str, Any]) -> date | None:
    """
    Extract the FAERS received date from a report.
    """
    return parse_faers_date(report.get("receivedate"))


def filter_reports_by_date(reports, start_date, end_date):
    """
    Keep reports with receivedate between start_date and end_date.
    """
    filtered = []
    for report in reports:
        report_date = get_report_received_date(report)

        if report_date is None:
            continue
        if start_date <= report_date <= end_date:
            filtered.append(report)

    return filtered


def split_recent_and_baseline(reports, today = None, recent_days = 90, baseline_days = 365):
    if today is None:
        today = date.today()

    recent_start = today - timedelta(days = recent_days)
    baseline_start = recent_start - timedelta(days = baseline_days)
    baseline_end = recent_start - timedelta(days = 1)

    recent_reports = filter_reports_by_date(reports, recent_start, today)
    baseline_reports = filter_reports_by_date(reports, baseline_start, baseline_end)


    return recent_reports, baseline_reports




