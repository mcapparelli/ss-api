from abc import ABC, abstractmethod
from typing import List
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance

class ISwap(ABC):
    @abstractmethod
    async def execute_swap(self, from_currency: str, to_currency: str, amount: float, balance: UserBalance) -> SwapResult:
        pass 