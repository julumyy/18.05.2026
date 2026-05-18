from src import manager
from src.models import Bill, Parameters, TenantSettlement, ApartmentSettlement, Transfer
from src.manager import Manager
import json


def test_validate_transfer_with_correct_amount():
    service = TransferService()
    service.set_transfer_limit(100, 1000)

    transfer = Transfer(500)

    assert service.validate_transfer(transfer) is True


def test_validate_transfer_with_too_small_amount():
    service = TransferService()
    service.set_transfer_limit(100, 1000)

    transfer = Transfer(50)

    assert service.validate_transfer(transfer) is False


def test_validate_transfer_with_too_large_amount():
    service = TransferService()
    service.set_transfer_limit(100, 1000)

    transfer = Transfer(1500)

    assert service.validate_transfer(transfer) is False


def test_set_transfer_limit_with_negative_values():
    service = TransferService()

    with pytest.raises(ValueError, match="nie mogą być ujemne"):
        service.set_transfer_limit(-1, 100)


def test_set_transfer_limit_with_min_greater_than_max():
    service = TransferService()

    with pytest.raises(ValueError, match="większa od maksymalnej"):
        service.set_transfer_limit(1000, 100)


def test_get_zly_transfer_returns_invalid_transfers():
    service = TransferService()
    service.set_transfer_limit(100, 1000)

    transfer1 = Transfer(50)     # błędny
    transfer2 = Transfer(500)    # poprawny
    transfer3 = Transfer(1500)   # błędny

    service.transfers = [transfer1, transfer2, transfer3]

    invalid_transfers = service.get_zly_transfer()

    assert len(invalid_transfers) == 2
    assert transfer1 in invalid_transfers
    assert transfer3 in invalid_transfers
    assert transfer2 not in invalid_transfers