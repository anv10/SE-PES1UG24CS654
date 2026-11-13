from hypothesis import given, strategies as st
from mobile_data_plan import parse_plan, usage_average, payable_bill

@given(st.text() | st.none())
def test_parse_plan_no_crash(s):

@given(st.text() | st.none())
def test_usage_average_no_crash(s):

@given(st.text() | st.none())
def test_payable_bill_no_crash(s):
