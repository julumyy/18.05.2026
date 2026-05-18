import pytest

from src import manager
from src.models import Bill, Parameters, TenantSettlement, ApartmentSettlement, Transfer
from src.manager import Manager
import json


def test_settlement_due_between_tanants_and_apartment():
    manager = Manager(Parameters())

    settlement: ApartmentSettlement = manager.get_settlement('apart-polanka', 2025, 1)
    
    tenants_settlements: list[TenantSettlement] = manager.create_tenants_settlements(settlement)
    assert len(tenants_settlements) == 3

    total_due = sum([tenant_settlement.total_due_pln for tenant_settlement in tenants_settlements])
    assert total_due == settlement.total_due_pln

def test_debtors_calculation():
    manager = Manager(Parameters())

    debtors = manager.get_debtors('apart-polanka', 2025, 1)
    assert len(debtors) == 0

    debtors = manager.get_debtors('apart-polanka', 2025, 2)
    assert len(debtors) == 3


def test_tax_calculation():
    manager = Manager(Parameters())
    
    tax = manager.calculate_tax(2025, 1, 0.085)
    assert tax == 638 # 0.085 * 7500.0

    tax = manager.calculate_tax(2025, 2, 0.085)
    assert tax == 0

def test_deposits_calculation():
    manager = Manager(Parameters())
    
    deposit_balance = manager.check_deposits()
    assert deposit_balance == -8700.0 # no deposit in transfers

    manager.transfers.append(Transfer(
        tenant='tenant-1',
        date='2025-01-01',
        settlement_year=None,
        settlement_month=None,
        amount_pln=1000.0,
        type='deposit'
    ))

    deposit_balance = manager.check_deposits()
    assert deposit_balance == -7700.0 # 1000.0 deposit in transfers

def test_annual_balance_calculation():
    manager = Manager(Parameters())
    
    annual_balance = manager.get_annual_balance(2025)
    assert annual_balance == 6490.0 # 7500.0 in transfers minus 910.0 in bills

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-02-15',
        settlement_year=2025,
        settlement_month=5,
        amount_pln=500.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-02-15',
        settlement_year=2025,
        settlement_month=5,
        amount_pln=4500.0,
        type='renovation'
    ))

    annual_balance = manager.get_annual_balance(2025)
    assert annual_balance == 1490.0 # 7500.0 in transfers minus 910.0 in bills minus new bills 500.0 and 4500.0

def test_apartment_has_any_bills():
    manager = Manager(Parameters())
    
    has_bills = manager.has_any_bills('apart-polanka', 2025, 1)
    assert has_bills == True

    has_bills = manager.has_any_bills('apart-polanka', 2025, 3)
    assert has_bills == False

def test_tych_klientow_nie_obslugujemy():
    manager = Manager(Parameters())

    assert manager.is_tenant_blacklisted("Józef Podgórski") == True

    assert manager.is_tenant_blacklisted("Jan Kowalski") == False

def test_ustawienia_limitow_przelewow():
    manager = Manager(Parameters())
    
    manager.set_transfer_limit(100.0, 5000.0)

    assert manager.min_transfer_amount == 100.0
    assert manager.max_transfer_amount == 5000.0

def test_blednych_limitow():
    manager = Manager(Parameters())
    
    with pytest.raises(ValueError, match="Minimalna i maksymalna kwota nie mogą być ujemne."):
        manager.set_transfer_limit(-10.0, 500.0)

    with pytest.raises(ValueError, match="Minimalna kwota nie może być większa od maksymalnej."):
        manager.set_transfer_limit(5000.0, 100.0)
    
def test_filtracja_zlych_przelewow():
    manager = Manager(Parameters())
    
    manager.set_transfer_limit(50.0, 5000.0)

    za_maly = Transfer(
        amount_pln=30.0,
        date='2025-01-01',
        settlement_year=2025,
        settlement_month=1,
        tenant='tenant-1'
)
    za_duzy = Transfer(
        amount_pln=6000.0,
        date='2025-01-01',
        settlement_year=2025,
        settlement_month=1,
        tenant='tenant-1'
)
    t_dobry = Transfer(
        amount_pln=150.0,
        date='2025-01-01',
        settlement_year=2025,
        settlement_month=1,
        tenant='tenant-1'
)


    manager.add_transfer(za_maly)
    manager.add_transfer(za_duzy)
    manager.add_transfer(t_dobry)

    zle = manager.get_zly_transfer()

    assert len(zle) == 2
    assert za_maly in zle
    assert za_duzy in zle
    assert t_dobry not in zle

if __name__ == "__main__":
    test_tych_klientow_nie_obslugujemy()

