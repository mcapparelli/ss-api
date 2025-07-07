import pytest
from unittest.mock import AsyncMock, MagicMock
from source.transfer.application.use_cases.deposit.use_case import DepositUseCase
from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer

@pytest.mark.asyncio
async def test_deposit_use_case():
    mock_db = AsyncMock()
    mock_user = MagicMock(spec=User)
    mock_user.id = "user-uuid"
    mock_balance = MagicMock(spec=UserBalance)
    mock_balance.amount = 0

    async def execute_side_effect(query):
        if "UserBalance" in str(query):
            class Result:
                def scalar_one_or_none(self_inner): return mock_balance
            return Result()
        else:
            class Result:
                def scalar_one_or_none(self_inner): return mock_user
            return Result()
    mock_db.execute.side_effect = execute_side_effect

    use_case = DepositUseCase(mock_db)
    result = await use_case.execute(user_id="user-uuid", amount=100, currency="USD")

    mock_balance.increment.assert_called_once_with("100")
    mock_db.add.assert_any_call(result)
    assert isinstance(result, Transfer)
    assert result.type == "DEPOSIT"
    assert result.user_id == "user-uuid"
    assert result.amount == "100"
    assert result.currency == "USD"