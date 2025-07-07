#!/usr/bin/env python3

import sys
import os
import unittest
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../')))

from source.transfer.application.use_cases.swap.strategies.fiat_to_fiat_strategy.fiat_to_fiat_strategy import FiatToFiatStrategy
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from source.common_types.currency_types import CurrencyType

class TestFiatToFiatStrategy(unittest.TestCase):
    
    def setUp(self):
        self.strategy = FiatToFiatStrategy()
        self.user_id = str(uuid.uuid4())
        
        # Mock balance with sufficient funds
        self.mock_balance = MagicMock(spec=UserBalance)
        self.mock_balance.user_id = self.user_id
        self.mock_balance.amount = Decimal("1000.0")
        
    @patch('source.transfer.application.use_cases.swap.strategies.fiat_to_fiat_strategy.fiat_to_fiat_strategy.PriceProvider.get_fiat_rate')
    async def test_usd_to_ars_swap(self, mock_fiat_rate):
        # Setup: USD → ARS conversion
        # 1 USD = 350 ARS 
        mock_fiat_rate.return_value = Decimal("350.0")
        
        # Execute: Convert 100 USD to ARS
        result = await self.strategy.execute_swap("USD", "ARS", 100.0, self.mock_balance)
        
        # Verify external call
        mock_fiat_rate.assert_called_once_with("USD", "ARS")
        
        # Verify result
        self.assertIsInstance(result, SwapResult)
        
        # Verify debit transfer (outgoing USD)
        debit = result.debit
        self.assertEqual(debit.amount, "-100.0")
        self.assertEqual(debit.currency, "USD")
        self.assertEqual(debit.user_id, self.user_id)
        
        # Verify credit transfer (incoming ARS)
        # 100 USD × 350 ARS/USD = 35,000 ARS
        credit = result.credit
        self.assertEqual(credit.amount, "35000.0")
        self.assertEqual(credit.currency, "ARS")
        self.assertEqual(credit.user_id, self.user_id)
        
        # Verify both transfers have same reference
        self.assertEqual(debit.reference, credit.reference)
        
    @patch('source.transfer.application.use_cases.swap.strategies.fiat_to_fiat_strategy.fiat_to_fiat_strategy.PriceProvider.get_fiat_rate')
    async def test_ars_to_usd_swap(self, mock_fiat_rate):
        # Setup: ARS → USD conversion
        # 350 ARS = 1 USD (reverse rate)
        mock_fiat_rate.return_value = Decimal("0.002857")  # 1/350
        
        # Execute: Convert 35,000 ARS to USD
        result = await self.strategy.execute_swap("ARS", "USD", 35000.0, self.mock_balance)
        
        # Verify external call
        mock_fiat_rate.assert_called_once_with("ARS", "USD")
        
        # Verify calculation
        # 35,000 ARS × 0.002857 USD/ARS = 100 USD
        credit = result.credit
        self.assertEqual(credit.amount, "100.0")
        self.assertEqual(credit.currency, "USD")
        
        # Verify debit
        debit = result.debit
        self.assertEqual(debit.amount, "-35000.0")
        self.assertEqual(debit.currency, "ARS")
        
    @patch('source.transfer.application.use_cases.swap.strategies.fiat_to_fiat_strategy.fiat_to_fiat_strategy.PriceProvider.get_fiat_rate')
    async def test_different_exchange_rates(self, mock_fiat_rate):
        # Test with different exchange rate
        mock_fiat_rate.return_value = Decimal("400.0")  # Higher rate
        
        # Execute
        result = await self.strategy.execute_swap("USD", "ARS", 50.0, self.mock_balance)
        
        # Verify calculation with different rate
        # 50 USD × 400 ARS/USD = 20,000 ARS
        credit = result.credit
        self.assertEqual(credit.amount, "20000.0")
        self.assertEqual(credit.currency, "ARS")
        
    @patch('source.transfer.application.use_cases.swap.strategies.fiat_to_fiat_strategy.fiat_to_fiat_strategy.PriceProvider.get_fiat_rate')
    async def test_decimal_precision(self, mock_fiat_rate):
        # Test with decimal amounts and rates
        mock_fiat_rate.return_value = Decimal("350.75")  # Precise rate
        
        # Execute with decimal amount
        result = await self.strategy.execute_swap("USD", "ARS", 0.5, self.mock_balance)
        
        # Verify precise calculation
        # 0.5 USD × 350.75 ARS/USD = 175.375 ARS
        credit = result.credit
        self.assertEqual(credit.amount, "175.375")
        
    async def test_insufficient_balance(self):
        # Setup balance with insufficient funds
        poor_balance = MagicMock(spec=UserBalance)
        poor_balance.user_id = self.user_id
        poor_balance.amount = Decimal("50.0")
        
        # Execute and verify exception
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("USD", "ARS", 100.0, poor_balance)
        
        self.assertEqual(str(context.exception), "Insufficient balance.")
        
    async def test_none_balance_handled(self):
        # Test when balance.amount is None
        none_balance = MagicMock(spec=UserBalance)
        none_balance.user_id = self.user_id
        none_balance.amount = None
        
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("USD", "ARS", 100.0, none_balance)
        
        self.assertEqual(str(context.exception), "Insufficient balance.")

if __name__ == "__main__":
    import asyncio
    
    # Helper to run async tests
    def run_async_test(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    # Patch test methods to run async
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFiatToFiatStrategy)
    for test in suite:
        if hasattr(test, '_testMethodName'):
            method_name = test._testMethodName
            if method_name.startswith('test_'):
                original_method = getattr(test, method_name)
                if asyncio.iscoroutinefunction(original_method):
                    setattr(test, method_name, lambda self, m=original_method: run_async_test(m(self)))
    
    unittest.main() 