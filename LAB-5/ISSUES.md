# Static Analysis Issues

Line numbers refer to the original file, as reported in `reports/*_before.txt`.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command built from input (B605) | Security (Bandit, High) | 58 | `os.system("echo ... " + filename)` passes a string to a shell, so a crafted `filename` could inject commands. | Removed the shell call and used `print()`, which gives the same message. |
| `eval()` on promo expression (B307 / W0123) | Security (Bandit Medium, Pylint) | 42 | `eval(promo_expr)` runs arbitrary Python from the caller. | Parse with `ast` and evaluate only numbers, `base_price`, and `+ - * / **`. Anything else raises `ValueError`. |
| Weak MD5 hash (B324) | Security (Bandit, High) | 47 | MD5 is broken for security use. | Kept MD5 so the ticket hash is unchanged, and passed `usedforsecurity=False` to mark it as a non-security identifier. A stronger hash such as SHA-256 would change the output. |
| Predictable PIN generator (B311) | Security (Bandit, Low) | 51 | `random.randint` is not cryptographically secure, so booking PINs can be predicted. | Use `secrets.randbelow` (`1000 + secrets.randbelow(9000)`, same 1000-9999 range). |
| Mutable default argument (W0102) | Bug (Pylint) | 15 | `order_history=[]` is created once and shared across calls, so history leaks between callers. | Default to `None` and create a new list inside the function. |
| Bare `except` with `pass` (B110 / W0702 / E722) | Error handling (Bandit, Pylint, Flake8) | 26-27 | Swallows every exception, including unrelated ones. | Replaced the try/except with an explicit `if seat_id in theater_seats` check. |
| Unused variables and import (W0612 / F841 / W0611 / F401) | Code quality | 6, 31, 41, 63 | `math`, `booking_fee`, `base_price` (as flagged) and the loop variable `seat` are never used. | Removed the dead code. `base_price` is now used by the safe evaluator. |
| Function name not snake_case (C0103) | Naming (Pylint) | 15 | `reserveSeat` breaks PEP 8 naming. | Renamed to `reserve_seat` and updated the caller. |
| Missing docstrings (C0116) | Documentation (Pylint) | 15, 23, 30, 40, 46, 50, 54, 61, 69 | Every function lacks a docstring. | Added one-line docstrings. |
| File opened without `with` or encoding (R1732 / W1514) | Resource handling (Pylint) | 55-57 | The file is not closed if `write` fails, and the encoding is not set. | Used `with open(..., encoding="utf-8")`. |
| `== None` comparison (C0121 / E711) | Style (Pylint, Flake8) | 32 | Should compare to `None` with `is`. | Changed to `is None`. |
| Shadowed global name (W0621) | Maintainability (Pylint) | 61 | The parameter `theater_seats` hides the module-level variable. | Renamed the parameter to `seats` and simplified the count with `sum()`. |
| Missing final newline (W292 / C0304) | Formatting (Flake8, Pylint) | 82 | File does not end with a newline. | Added the newline. |

## Not flagged by the tools

`main()` prints the hardcoded `BOX_OFFICE_SECRET_PASS_2026` to the console (line 70 and 79 in the original). Bandit did not flag it, but a secret should not be hardcoded or printed. I left it alone because changing it would change what the program does.
