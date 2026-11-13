"""Mobile Data Plan - hardened version (Lab 7: Fuzz Testing).

Every public function validates its input defensively and returns ``None``
for anything it cannot process safely, instead of raising an exception or
returning a nonsensical value (NaN, infinity, negative amounts, ...).

Bugs found by Hypothesis fuzzing in the original version and fixed here:

parse_plan
  * None / non-string input            -> AttributeError
  * missing or extra ':'               -> ValueError (unpacking)
  * non-numeric data amount            -> ValueError from float()
  * 'nan', 'inf', negative GB accepted -> nonsensical plan
  * empty plan name accepted

usage_average
  * None / non-string input            -> AttributeError
  * empty string / empty fields ('1,,3')-> ValueError from int()
  * non-numeric values                 -> ValueError from int()
  * huge numbers (> 4300 digits)       -> ValueError (int str-digit limit)
  * negative usage accepted
  * '//' floor division silently truncated the average (0,1 -> 0)

payable_bill
  * None / non-string input            -> AttributeError
  * missing or extra '|'               -> ValueError (unpacking)
  * non-numeric bill/discount          -> ValueError from float()
  * 'nan' -> max(nan, 0) returned nan; 'inf' returned inf
  * huge bills overflowed to inf (1.6e308 * 1.18)
  * negative bill / negative discount accepted (discount *increased* bill)
"""

import math

GST_RATE = 1.18


def _to_finite_float(value):
    """Convert a string to a finite float, or return None."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(number):
        return None
    return number


def parse_plan(text):
    """Parse 'plan:gb' into (Plan Name, gb). Returns None on invalid input."""
    if not isinstance(text, str):
        return None

    parts = text.split(':')
    if len(parts) != 2:
        return None

    plan = parts[0].strip()
    gb = _to_finite_float(parts[1].strip())
    if not plan or gb is None or gb < 0:
        return None

    return plan.title(), gb


def usage_average(usage_csv):
    """Average of comma-separated daily usage values in MB.

    Returns the mean rounded to 2 decimals, or None on invalid input.
    """
    if not isinstance(usage_csv, str):
        return None

    values = []
    for raw in usage_csv.split(','):
        raw = raw.strip()
        if not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            return None
        if value < 0:
            return None
        values.append(value)

    if not values:
        return None

    return round(sum(values) / len(values), 2)


def payable_bill(text):
    """Bill after 18% GST minus discount, from 'bill|discount'.

    Returns the amount rounded to 2 decimals (never below 0),
    or None on invalid input.
    """
    if not isinstance(text, str):
        return None

    parts = text.split('|')
    if len(parts) != 2:
        return None

    bill = _to_finite_float(parts[0].strip())
    discount = _to_finite_float(parts[1].strip())
    if bill is None or discount is None or bill < 0 or discount < 0:
        return None

    total = bill * GST_RATE - discount
    if not math.isfinite(total):
        return None

    return round(max(total, 0.0), 2)


def main():
    print("==== Running parse_plan ====")
    user_input = input("Enter plan:data in GB (e.g. standard:5): ")
    result = parse_plan(user_input)
    if result is None:
        print("Invalid input! Expected format plan:GB, e.g. standard:5")
    else:
        print("Plan and Data:", result)

    print("\n==== Running usage_average ====")
    user_input = input("Enter daily usage in MB as CSV (e.g. 300,450,800): ")
    result = usage_average(user_input)
    if result is None:
        print("Invalid input! Expected non-negative whole numbers, "
              "e.g. 300,450,800")
    else:
        print("Average Usage:", result)

    print("\n==== Running payable_bill ====")
    user_input = input("Enter bill|discount (e.g. 399|50): ")
    result = payable_bill(user_input)
    if result is None:
        print("Invalid input! Expected non-negative numbers bill|discount, "
              "e.g. 399|50")
    else:
        print("Payable Bill:", result)


if __name__ == "__main__":
    main()
