from datetime import datetime
from dateutil.relativedelta import relativedelta

def calc_date_range(
    start_months_ago: int = 3,
    end_on_last_day: bool = True,
    reference_date: datetime.date = None,
):
    """Calculate a date range label for a period in months relative to a reference date.

    Returns start and end dates for a period starting from the first day of
    `start_months_ago` months ago to either the first or last day of the month
    prior to the reference date (or today if no reference date is given).

    Args:
        start_months_ago: How many months ago to start the date range. Default is 3.
        end_on_last_day: If True, the end date is set to the last day of the last month.
            If False, the end date is the first day of the last month.
        reference_date: Optional reference date. Defaults to today.

    Returns:
        dict[str, str]: Dictionary with keys:
            - 'start_date_gee': Start date in YYYY-MM-DD format.
            - 'end_date_gee': End date in YYYY-MM-DD format.
    """
    if reference_date is None:
        reference_date = datetime.today()
    
    this_month_first = reference_date.replace(day=1) #first day of this month

    # Start date: first day of 'start_months_ago' months ago
    start_date = this_month_first - relativedelta(months=start_months_ago)

    # End date: first or last day of the month before reference date
    end_date = this_month_first - relativedelta(months=1) # first day of prior month
    if end_on_last_day:
        end_date = this_month_first - relativedelta(days=1)  # last day of prior month

    # Format for labels and GEE
    start_date_gee = start_date.strftime("%Y-%m-%d")
    end_date_gee = end_date.strftime("%Y-%m-%d")

    return {
            "start_date_gee": start_date_gee,
            "end_date_gee": end_date_gee
        }

def enforce_two_month_lag(date_range: dict) -> dict:
    """
    Ensure end date is at least two months behind today.
    """

    new = date_range.copy()

    # --- cutoff month 
    cutoff = datetime.today()- relativedelta(months=2)
    cutoff = cutoff.replace(hour=0,
                            minute=0,
                            second=0,
                            microsecond=0)

    # --- parse existing end_label
    end_date = datetime.strptime(new["end_date_gee"], "%Y-%m-%d")

    if end_date > cutoff:

        # last day of month for GEE
        last_day = cutoff - relativedelta(days=1)
        last_day = last_day.replace(day=1)
        new["end_date_gee"] = last_day.strftime("%Y-%m-%d")

    return new