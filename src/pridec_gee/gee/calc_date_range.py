from datetime import datetime
from dateutil.relativedelta import relativedelta

def calc_date_range(start_months_ago = 3, end_on_last_day=False, reference_date=None):
    """
    Returns date range labels for a period starting from the first day of `start_months_ago` months ago
    to either the first or last day of the month prior to reference date.

    Args:
        start_months_ago (int): How many months ago to start data collection. Default is 3.
        end_on_last_day (bool): If True, sets the end date to the last day of end_months_ago month.
                                If False, uses the first day of end_months_ago prior month.
        reference_date (datetime, optional): Use this as the reference date instead of today.

    Returns:
        dict: (start_label, end_label, start_date_gee, end_date_gee)
    """
    if reference_date is None:
        reference_date = datetime.today()
    
    this_month_first = reference_date.replace(day=1)

    # Start date: first day of 'start_months_ago' months ago
    start_date = this_month_first - relativedelta(months=start_months_ago)

    # End date: first or last day of the 'end_months_ago' month
    end_date = this_month_first - relativedelta(months=1) # first day of prior month
    if end_on_last_day:
        end_date = end_date + relativedelta(months=1) - relativedelta(days=1)  # last day of prior month

    # Format for labels and GEE
    start_label = start_date.strftime("%Y%m")
    end_label = end_date.strftime("%Y%m")
    start_date_gee = start_date.strftime("%Y-%m-%d")
    end_date_gee = end_date.strftime("%Y-%m-%d")

    return {
            "start_label": start_label,
            "end_label": end_label,
            "start_date_gee": start_date_gee,
            "end_date_gee": end_date_gee
        }