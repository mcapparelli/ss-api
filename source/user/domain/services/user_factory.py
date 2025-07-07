from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.common_types import Currency

def create_user(name: str) -> User:
    user = User(name=name)
    for currency in Currency.valid_currencies():
        balance = UserBalance(currency=currency, amount=0)
        user.balances.append(balance)
    return user