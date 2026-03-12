
from datetime import datetime

from pridec_gee import calc_date_range

def test_first_day_appears():
    out_date = calc_date_range(start_months_ago = 3,
                               end_on_last_day = True,
                               reference_date = datetime(year=2019,month=12,day=20))
    assert out_date['start_date_gee']=='2019-09-01'
    assert out_date['end_date_gee']=='2019-11-30'
