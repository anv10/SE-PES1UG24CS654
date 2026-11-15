import pytest
from mobile_data_plan import overage_charge, recharge_allowed, validity_status


# ---------- overage_charge ----------

def test_unknown_plan():
    with pytest.raises(ValueError):
        overage_charge("gold", 5, False, False)


def test_negative_usage():
    with pytest.raises(ValueError):
        overage_charge("basic", -1, False, False)


def test_within_included_data():
    assert overage_charge("standard", 3, False, False) == 0


def test_exactly_at_limit():
    # extra == 0 should still be free
    assert overage_charge("premium", 10, True, False) == 0


def test_loyal_bonus_gb():
    # loyal non-premium user gets 1 extra GB, so 6 GB on standard is free
    assert overage_charge("standard", 6, False, True) == 0


def test_loyal_premium_no_bonus():
    # premium users don't get the loyalty GB
    assert overage_charge("premium", 11, False, True) == 15


def test_small_overage_home():
    assert overage_charge("basic", 5, False, False) == 3 * 15


def test_small_overage_roaming():
    assert overage_charge("basic", 5, True, False) == 3 * 40


def test_overage_exactly_10_extra():
    # extra == 10 is not "heavy", normal rate applies
    assert overage_charge("basic", 12, False, False) == 10 * 15


def test_heavy_overage_home():
    # extra > 10 at home: 15 + 10 = 25/GB, no roaming surcharge
    assert overage_charge("basic", 20, False, False) == 18 * 25


def test_heavy_overage_roaming():
    # extra > 10 roaming: 40 + 10 + 5 = 55/GB
    assert overage_charge("standard", 20, True, True) == 14 * 55


# ---------- recharge_allowed ----------

def test_kyc_pending_small_amount():
    assert recharge_allowed(200, 5, True) is True


def test_kyc_pending_large_amount():
    assert recharge_allowed(201, 0, True) is False


def test_amount_at_limit():
    assert recharge_allowed(2000, 0, False) is True


def test_amount_over_limit():
    assert recharge_allowed(2001, 0, False) is False


def test_recharge_allowed():
    assert recharge_allowed(500, 1, False) is True


def test_pending_recharges_at_limit():
    assert recharge_allowed(500, 2, False) is True


def test_too_many_pending_recharges():
    assert recharge_allowed(500, 3, False) is False


# ---------- validity_status ----------

def test_prepaid_active():
    assert validity_status(0, True, False) == "active"


def test_prepaid_with_addon_active():
    assert validity_status(2, True, True) == "active"


def test_prepaid_with_addon_grace():
    # addon pushes cutoff to 2, so 1 day left is grace
    assert validity_status(1, True, True) == "grace"


def test_postpaid_active():
    assert validity_status(3, False, False) == "active"


def test_postpaid_grace():
    assert validity_status(2, False, False) == "grace"


def test_postpaid_with_addon_grace_lower_edge():
    # cutoff = 5, grace goes down to 5 - 15 = -10
    assert validity_status(-10, False, True) == "grace"


def test_postpaid_expired():
    assert validity_status(-13, False, False) == "expired"


def test_prepaid_expired():
    assert validity_status(-16, True, False) == "expired"
