from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_date_range(end_months_ago=1, start_months_ago = 3, end_on_last_day=False, reference_date=None):
    """
    Returns date range labels for a period starting from the first day of `months_ago` months ago
    to either the first or last day of the prior month.

    Args:
        end_months_ago (int): How many months ago to end data collection. Default is 1.
        start_months_ago (int): How many months ago to start data collection. Default is 3.
        end_on_last_day (bool): If True, sets the end date to the last day of the prior month.
                                If False, uses the first day of the prior month.
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
    if end_on_last_day:
        prior_month_first = this_month_first - relativedelta(months=end_months_ago)
        end_date = prior_month_first + relativedelta(day=31)  # last day of prior month
    else:
        end_date = this_month_first - relativedelta(months=end_months_ago)  # first day of prior month

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