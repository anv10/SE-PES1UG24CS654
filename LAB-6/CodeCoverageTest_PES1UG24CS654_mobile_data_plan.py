import pytest
from mobile_data_plan import overage_charge, recharge_allowed, validity_status


# ---------- overage_charge ----------

def test_within_included_data():
    assert overage_charge("standard", 3, False, False) == 0


def test_unknown_plan():
    with pytest.raises(ValueError):
        overage_charge("gold", 5, False, False)


def test_negative_usage():
    with pytest.raises(ValueError):
        overage_charge("basic", -1, False, False)


def test_small_overage_home():
    # basic gives 2 GB, used 5 -> 3 GB extra at 15/GB
    assert overage_charge("basic", 5, False, False) == 45


def test_heavy_overage_roaming_loyal():
    # standard 5 GB + 1 loyalty GB = 6, used 20 -> 14 extra
    # roaming 40 + 10 heavy + 5 roaming heavy = 55/GB
    assert overage_charge("standard", 20, True, True) == 14 * 55


# ---------- recharge_allowed ----------

def test_recharge_allowed():
    assert recharge_allowed(500, 1, False) is True


def test_recharge_kyc_pending():
    assert recharge_allowed(150, 0, True) is True


def test_recharge_amount_too_high():
    assert recharge_allowed(2500, 0, False) is False


# ---------- validity_status ----------

def test_prepaid_with_addon_active():
    assert validity_status(5, True, True) == "active"


def test_postpaid_grace():
    assert validity_status(0, False, False) == "grace"


def test_expired():
    assert validity_status(-20, True, False) == "expired"
