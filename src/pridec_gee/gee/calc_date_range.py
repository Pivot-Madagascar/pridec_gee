from datetime import datetime
from dateutil.relativedelta import relativedelta

def calc_date_range(start_months_ago = 3, end_on_last_day=True, reference_date=None):
    """
    Returns date range labels for a period starting from the first day of `start_months_ago` months ago
    to either the first or last day of the month prior to reference date.

    Args:
        start_months_ago (int): How many months ago to start data collection. Default is 3.
        end_on_last_day (bool): If True, sets the end date to the last day of end_months_ago month.
                                If False, uses the first day of end_months_ago prior month.
        reference_date (datetime, optional): Use this as the reference date instead of today.

    Returns:
        dict: (start_date_gee, end_date_gee)
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