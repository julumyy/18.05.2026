import pytest

from src.manager import Manager
from src.models import Transfer, Parameters


def create_manager():
    parameters = Parameters(
        rent=1000,
        internet=100,
        electricity=200,
        water=150
    )
    return Manager(parameters)


def make_transfer(amount: int):
    return Transfer(
        amount_pln=amount,
        date="2026-05-19",   # <- musi być string
        settlement_year=2026,
        settlement_month=5,
        tenant="test_tenant"
    )


def test_validate_transfer_with_correct_amount():
    service = create_manager()
    service.set_transfer_limit(100, 1000)

    transfer = make_transfer(500)

    assert service.validate_transfer(transfer) is True


def test_validate_transfer_with_too_small_amount():
    service = create_manager()
    service.set_transfer_limit(100, 1000)

    transfer = make_transfer(50)

    assert service.validate_transfer(transfer) is False


def test_validate_transfer_with_too_large_amount():
    service = create_manager()
    service.set_transfer_limit(100, 1000)

    transfer = make_transfer(1500)

    assert service.validate_transfer(transfer) is False


def test_set_transfer_limit_with_negative_values():
    service = create_manager()

    with pytest.raises(ValueError, match="nie mogą być ujemne"):
        service.set_transfer_limit(-1, 100)


def test_set_transfer_limit_with_min_greater_than_max():
    service = create_manager()

    with pytest.raises(ValueError, match="większa od maksymalnej"):
        service.set_transfer_limit(1000, 100)


def test_get_zly_transfer_returns_invalid_transfers():
    service = create_manager()
    service.set_transfer_limit(100, 1000)

    transfer1 = make_transfer(50)
    transfer2 = make_transfer(500)
    transfer3 = make_transfer(1500)

    service.transfers = [transfer1, transfer2, transfer3]

    invalid_transfers = service.get_zly_transfer()

    assert len(invalid_transfers) == 2
    assert transfer1 in invalid_transfers
    assert transfer3 in invalid_transfers
    assert transfer2 not in invalid_transfers