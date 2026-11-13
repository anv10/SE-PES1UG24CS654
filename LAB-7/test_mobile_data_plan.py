"""Hypothesis fuzz tests for mobile_data_plan.py (Lab 7)."""

import math

import pytest
from hypothesis import given, settings, strategies as st

from mobile_data_plan import parse_plan, usage_average, payable_bill

FUZZ = settings(max_examples=500, deadline=None)

# Numbers written as strings, including the nasty ones: nan, inf, -0.0,
# negatives, 1e308, and garbage that is not a number at all.
number_text = st.one_of(
    st.floats(allow_nan=True, allow_infinity=True).map(repr),
    st.integers().map(str),
    st.sampled_from(["nan", "inf", "-inf", "1e309", "", " ", "abc", "1,5"]),
    st.text(max_size=10),
)
# Non-negative values that a real user could type.
sane_amount = st.floats(min_value=0, max_value=1e6, allow_nan=False)
plan_name = st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=1,
                    max_size=15).filter(lambda s: s.strip())


# ---------------------------------------------------------------------------
# 1. "Must not crash" tests  (completed starter code)
# ---------------------------------------------------------------------------

@FUZZ
@given(st.text() | st.none())
def test_parse_plan_no_crash(s):
    try:
        parse_plan(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_plan crashed with: {e!r}"


@FUZZ
@given(st.text() | st.none())
def test_usage_average_no_crash(s):
    try:
        usage_average(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"usage_average crashed with: {e!r}"


@FUZZ
@given(st.text() | st.none())
def test_payable_bill_no_crash(s):
    try:
        payable_bill(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"payable_bill crashed with: {e!r}"


# ---------------------------------------------------------------------------
# 2. Structured fuzzing: inputs in the *right shape* but with edge-case
#    values. Output must be None (rejected) or a sensible value.
# ---------------------------------------------------------------------------

@FUZZ
@given(st.text(max_size=15), number_text)
def test_parse_plan_output_is_sane(name, gb):
    result = parse_plan(f"{name}:{gb}")
    if result is not None:
        plan, data = result
        assert isinstance(plan, str) and plan.strip(), "empty plan name"
        assert math.isfinite(data), f"non-finite data amount {data}"
        assert data >= 0, f"negative data amount {data}"


@FUZZ
@given(st.lists(st.one_of(st.integers().map(str), number_text), max_size=8))
def test_usage_average_output_is_sane(items):
    result = usage_average(",".join(items))
    if result is not None:
        assert math.isfinite(result), f"non-finite average {result}"
        assert result >= 0, f"negative average {result}"


@FUZZ
@given(number_text, number_text)
def test_payable_bill_output_is_sane(bill, discount):
    result = payable_bill(f"{bill}|{discount}")
    if result is not None:
        assert math.isfinite(result), f"non-finite bill {result}"
        assert result >= 0, f"negative bill {result}"
        # A discount must never make the bill bigger than bill + GST.
        assert result <= float(bill) * 1.18 + 0.01, "discount increased bill"


# ---------------------------------------------------------------------------
# 3. Valid inputs must still give the correct answer (no over-rejection).
# ---------------------------------------------------------------------------

@FUZZ
@given(plan_name, sane_amount)
def test_parse_plan_valid_input(name, gb):
    assert parse_plan(f" {name} : {gb!r} ") == (name.strip().title(), gb)


@FUZZ
@given(st.lists(st.integers(min_value=0, max_value=10**6), min_size=1,
                max_size=30))
def test_usage_average_valid_input(values):
    result = usage_average(", ".join(map(str, values)))
    assert result == pytest.approx(sum(values) / len(values), abs=0.006)


@FUZZ
@given(sane_amount, sane_amount)
def test_payable_bill_valid_input(bill, discount):
    expected = max(bill * 1.18 - discount, 0)
    assert payable_bill(f"{bill!r}|{discount!r}") == pytest.approx(
        expected, abs=0.006)


# ---------------------------------------------------------------------------
# 4. Regression tests for the minimal failing inputs Hypothesis reported.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("func, bad_input", [
    (parse_plan, None), (parse_plan, ""), (parse_plan, "standard"),
    (parse_plan, "a:b:c"), (parse_plan, "standard:abc"),
    (parse_plan, "standard:nan"), (parse_plan, "standard:inf"),
    (parse_plan, "standard:-5"), (parse_plan, ":5"),
    (usage_average, None), (usage_average, ""), (usage_average, "1,,3"),
    (usage_average, "a,b"), (usage_average, "-5,10"),
    (usage_average, "9" * 5000),
    (payable_bill, None), (payable_bill, ""), (payable_bill, "399"),
    (payable_bill, "1|2|3"), (payable_bill, "abc|10"),
    (payable_bill, "nan|0"), (payable_bill, "inf|0"),
    (payable_bill, "1.6e308|0"), (payable_bill, "-100|0"),
    (payable_bill, "100|-50"),
])
def test_known_bad_inputs_are_rejected(func, bad_input):
    assert func(bad_input) is None


def test_handout_examples():
    assert parse_plan("standard:5") == ("Standard", 5.0)
    assert usage_average("300,450,800") == 516.67
    assert payable_bill("399|50") == 420.82
    assert payable_bill("10|500") == 0
