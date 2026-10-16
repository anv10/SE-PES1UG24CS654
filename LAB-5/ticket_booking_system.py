"""Movie theater ticket booking and seating management module."""

import ast
import hashlib
import operator
import secrets
import math

theater_seats = {
    "A1": {"tier": "Standard", "price": 12.0, "is_sold": False},
    "A2": {"tier": "Standard", "price": 12.0, "is_sold": True},
    "B1": {"tier": "Premium", "price": 20.0, "is_sold": False},
}


def reserveSeat(seat_id, customer, order_history=[]):
    if seat_id not in theater_seats or theater_seats[seat_id]["is_sold"]:
        return False
    theater_seats[seat_id]["is_sold"] = True
    order_history.append("Reserved seat %s for customer %s" % (seat_id, customer))
    return True


def cancel_seat(seat_id):
    if seat_id in theater_seats:
        theater_seats[seat_id]["is_sold"] = False


def check_seat_status(seat_id):
    booking_fee = 1.50
    if theater_seats.get(seat_id) == None:
        return False
    if not theater_seats[seat_id]["is_sold"]:
        return True
    else:
        return False


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(node, base_price):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, base_price)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_price":
        return base_price
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](
            _safe_eval(node.left, base_price),
            _safe_eval(node.right, base_price),
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand, base_price))
    raise ValueError("Unsupported promo expression")


def compute_discounted_price(seat_id, promo_expr):
    base_price = theater_seats[seat_id]["price"]
    tree = ast.parse(promo_expr, mode="eval")
    return _safe_eval(tree, base_price)


def generate_ticket_hash(ticket_code):
    return hashlib.md5(ticket_code.encode(), usedforsecurity=False).hexdigest()


def generate_booking_pin():
    return 1000 + secrets.randbelow(9000)


def export_seating_chart(filename="seating_chart.txt"):
    f = open(filename, "w")
    f.write(str(theater_seats))
    f.close()
    print("Seating chart exported to:", filename)


def get_theater_summary(theater_seats):
    sold_count = 0
    for seat, details in theater_seats.items():
        if details["is_sold"]:
            sold_count += 1
    return sold_count


def main():
    box_office_key = "BOX_OFFICE_SECRET_PASS_2026"
    reserveSeat("A1", "Sarah Connor")
    cancel_seat("A2")
    print("Is B1 available:", check_seat_status("B1"))
    print("Promo price:", compute_discounted_price("B1", "base_price * 0.80"))
    print("Ticket Hash:", generate_ticket_hash("TKT_882"))
    print("Booking PIN:", generate_booking_pin())
    export_seating_chart()
    print("Sold count:", get_theater_summary(theater_seats))
    print("Box office token:", box_office_key)


main()