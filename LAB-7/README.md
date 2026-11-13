# Lab 7 – Fuzzing for Input Validation Bugs

Assigned app: **L6_L7_45 – Mobile Data Plan** (`mobile_data_plan.py`),
fuzzed with [Hypothesis](https://hypothesis.readthedocs.io/) + pytest.

| File | What it is |
|------|------------|
| `mobile_data_plan.py` | **Fixed** application (hardened input validation) |
| `test_mobile_data_plan.py` | **Completed** Hypothesis test file (35 tests) |
| `original/` | Original buggy script + starter test file (for reference) |

## Run

```bash
pip install hypothesis pytest
python mobile_data_plan.py
pytest test_mobile_data_plan.py
```

Results: buggy version **33 failed / 2 passed** → fixed version **35 passed**.

## Bugs fixed (16)

* **parse_plan** – crash on `None`, missing/extra `:`, non-numeric GB; accepted `nan`/`inf`/negative GB and empty plan names.
* **usage_average** – crash on `None`, empty string, empty fields (`1,,3`), non-numbers, >4300-digit numbers; accepted negative usage; `//` truncated the average.
* **payable_bill** – crash on `None`, missing/extra `|`, non-numbers; returned `nan`/`inf`; overflow on huge bills; negative bill accepted and a negative discount *increased* the bill.

Every function now returns `None` for invalid input, and `main()` prints a friendly "Invalid input!" message instead of crashing.
