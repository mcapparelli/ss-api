from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.common_types import CurrencyType

def create_user(name: str) -> User:
    user = User(name=name)
    for currency in CurrencyType.valid_currencies():
        balance = UserBalance(currency=currency.value, amount=0)
        user.balances.append(balance)
    return user