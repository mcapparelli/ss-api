#!/usr/bin/env python3

import sys
import os
import unittest
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../')))

from source.transfer.application.use_cases.swap.strategies.crypto_to_crypto.crypto_to_crypto import CryptoToCryptoStrategy
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.application.use_cases.swap.swap_result import SwapResult

class TestCryptoToCryptoStrategy(unittest.TestCase):
    
    def setUp(self):
        self.strategy = CryptoToCryptoStrategy()
        self.user_id = str(uuid.uuid4())
        
        # Mock balance with sufficient funds
        self.mock_balance = MagicMock(spec=UserBalance)
        self.mock_balance.user_id = self.user_id
        self.mock_balance.amount = Decimal("1.0")
        
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_crypto.crypto_to_crypto.PriceProvider.get_crypto_rate')
    async def test_successful_swap(self, mock_get_rate):
        # Setup
        mock_get_rate.return_value = Decimal("15.5")  # 1 BTC = 15.5 ETH
        amount = 0.1  # 0.1 BTC
        
        # Execute
        result = await self.strategy.execute_swap("BTC", "ETH", amount, self.mock_balance)
        
        # Verify external call
        mock_get_rate.assert_called_once_with("BTC", "ETH")
        
        # Verify result structure
        self.assertIsInstance(result, SwapResult)
        self.assertIsNotNone(result.debit)
        self.assertIsNotNone(result.credit)
        
        # Verify debit transfer (outgoing BTC)
        debit = result.debit
        self.assertEqual(debit.amount, "-0.1")  # Negative amount
        self.assertEqual(debit.currency, "BTC")
        self.assertEqual(debit.user_id, self.user_id)
        self.assertEqual(debit.type, "SWAP")
        self.assertEqual(debit.status, "CONFIRMED")
        
        # Verify credit transfer (incoming ETH)
        credit = result.credit
        self.assertEqual(credit.amount, "1.55")  # 0.1 * 15.5 = 1.55
        self.assertEqual(credit.currency, "ETH")
        self.assertEqual(credit.user_id, self.user_id)
        self.assertEqual(credit.type, "SWAP")
        self.assertEqual(credit.status, "CONFIRMED")
        
        # Verify same reference
        self.assertEqual(debit.reference, credit.reference)
        self.assertIsNotNone(debit.reference)
        
    async def test_insufficient_balance(self):
        # Setup balance with insufficient funds
        poor_balance = MagicMock(spec=UserBalance)
        poor_balance.user_id = self.user_id
        poor_balance.amount = Decimal("0.05")  # Only 0.05 BTC
        
        # Execute and verify exception
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("BTC", "ETH", 0.1, poor_balance)
        
        self.assertEqual(str(context.exception), "Insufficient balance.")
        
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_crypto.crypto_to_crypto.PriceProvider.get_crypto_rate')
    async def test_exchange_rate_calculation(self, mock_get_rate):
        # Test with different exchange rate
        mock_get_rate.return_value = Decimal("0.065")  # 1 ETH = 0.065 BTC
        
        result = await self.strategy.execute_swap("ETH", "BTC", 2.0, self.mock_balance)
        
        # Verify calculation: 2.0 ETH * 0.065 = 0.13 BTC
        self.assertEqual(result.credit.amount, "0.13")
        self.assertEqual(result.debit.amount, "-2.0")
        
    async def test_zero_balance_edge_case(self):
        # Test with exactly zero balance
        zero_balance = MagicMock(spec=UserBalance)
        zero_balance.user_id = self.user_id
        zero_balance.amount = Decimal("0")
        
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("BTC", "ETH", 0.001, zero_balance)
        
        self.assertEqual(str(context.exception), "Insufficient balance.")
        
    async def test_none_balance_handled(self):
        # Test when balance.amount is None
        none_balance = MagicMock(spec=UserBalance)
        none_balance.user_id = self.user_id
        none_balance.amount = None  # Could happen with new accounts
        
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("BTC", "ETH", 0.001, none_balance)
        
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCryptoToCryptoStrategy)
    for test in suite:
        if hasattr(test, '_testMethodName'):
            method_name = test._testMethodName
            if method_name.startswith('test_'):
                original_method = getattr(test, method_name)
                if asyncio.iscoroutinefunction(original_method):
                    setattr(test, method_name, lambda self, m=original_method: run_async_test(m(self)))
    
    unittest.main() 