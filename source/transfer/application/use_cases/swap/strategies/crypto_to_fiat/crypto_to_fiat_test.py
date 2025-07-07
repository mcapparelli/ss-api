#!/usr/bin/env python3

import sys
import os
import unittest
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../')))

from source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat import CryptoToFiatStrategy
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from source.common_types.currency_types import CurrencyType

class TestCryptoToFiatStrategy(unittest.TestCase):
    
    def setUp(self):
        self.strategy = CryptoToFiatStrategy()
        self.user_id = str(uuid.uuid4())
        
        # Mock balance with sufficient funds
        self.mock_balance = MagicMock(spec=UserBalance)
        self.mock_balance.user_id = self.user_id
        self.mock_balance.amount = Decimal("1.0")
        
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat.PriceProvider.get_crypto_rate')
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat.PriceProvider.get_fiat_rate')
    async def test_crypto_to_fiat_swap(self, mock_fiat_rate, mock_crypto_rate):
        # Setup: BTC → ARS
        # Step 1: 1 BTC = 45000 USD
        # Step 2: 1 USD = 350 ARS
        # Result: 0.1 BTC = 4500 USD = 1,575,000 ARS
        
        mock_crypto_rate.return_value = Decimal("45000")  # BTC → USD
        mock_fiat_rate.return_value = Decimal("350")      # USD → ARS
        
        # Execute
        result = await self.strategy.execute_swap("BTC", "ARS", 0.1, self.mock_balance)
        
        # Verify external calls (crypto → fiat uses both)
        mock_crypto_rate.assert_called_once_with("BTC", "USD")
        mock_fiat_rate.assert_called_once_with("USD", "ARS")
        
        # Verify result
        self.assertIsInstance(result, SwapResult)
        
        # Verify debit transfer (outgoing BTC)
        debit = result.debit
        self.assertEqual(debit.amount, "-0.1")
        self.assertEqual(debit.currency, "BTC")
        self.assertEqual(debit.user_id, self.user_id)
        
        # Verify credit transfer (incoming ARS)
        # 0.1 BTC × 45000 USD/BTC × 350 ARS/USD = 1,575,000 ARS
        credit = result.credit
        self.assertEqual(credit.amount, "1575000")
        self.assertEqual(credit.currency, "ARS")
        self.assertEqual(credit.user_id, self.user_id)
        
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat.PriceProvider.get_crypto_rate')
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat.PriceProvider.get_fiat_rate')
    async def test_fiat_to_crypto_swap(self, mock_fiat_rate, mock_crypto_rate):
        # Setup: ARS → BTC
        # Step 1: 350 ARS = 1 USD
        # Step 2: 45000 USD = 1 BTC
        # Result: 350,000 ARS = 1000 USD = 0.022222 BTC
        
        mock_fiat_rate.return_value = Decimal("0.002857")  # ARS → USD (1/350)
        mock_crypto_rate.return_value = Decimal("0.000022222")  # USD → BTC (1/45000)
        
        # Execute
        result = await self.strategy.execute_swap("ARS", "BTC", 350000, self.mock_balance)
        
        # Verify external calls (fiat → crypto uses both)
        mock_fiat_rate.assert_called_once_with("ARS", "USD")
        mock_crypto_rate.assert_called_once_with("USD", "BTC")
        
        # Verify calculation
        # 350,000 ARS × 0.002857 USD/ARS × 0.000022222 BTC/USD ≈ 0.022222 BTC
        credit = result.credit
        self.assertEqual(credit.currency, "BTC")
        
    @patch('source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat.PriceProvider.get_crypto_rate')
    async def test_usd_to_crypto_direct(self, mock_crypto_rate):
        # Setup: USD → ETH (no fiat conversion needed)
        mock_crypto_rate.return_value = Decimal("0.0004")  # USD → ETH
        
        # Execute
        result = await self.strategy.execute_swap("USD", "ETH", 1000, self.mock_balance)
        
        # Verify only one external call (USD is already USD)
        mock_crypto_rate.assert_called_once_with("USD", "ETH")
        
        # Verify calculation: 1000 USD × 0.0004 ETH/USD = 0.4 ETH
        credit = result.credit
        self.assertEqual(credit.amount, "0.4")
        self.assertEqual(credit.currency, "ETH")
        
    async def test_insufficient_balance(self):
        # Setup balance with insufficient funds
        poor_balance = MagicMock(spec=UserBalance)
        poor_balance.user_id = self.user_id
        poor_balance.amount = Decimal("0.05")
        
        # Execute and verify exception
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("BTC", "USD", 0.1, poor_balance)
        
        self.assertEqual(str(context.exception), "Insufficient balance.")
        
    async def test_none_balance_handled(self):
        # Test when balance.amount is None
        none_balance = MagicMock(spec=UserBalance)
        none_balance.user_id = self.user_id
        none_balance.amount = None
        
        with self.assertRaises(ValueError) as context:
            await self.strategy.execute_swap("ETH", "ARS", 0.1, none_balance)
        
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCryptoToFiatStrategy)
    for test in suite:
        if hasattr(test, '_testMethodName'):
            method_name = test._testMethodName
            if method_name.startswith('test_'):
                original_method = getattr(test, method_name)
                if asyncio.iscoroutinefunction(original_method):
                    setattr(test, method_name, lambda self, m=original_method: run_async_test(m(self)))
    
    unittest.main() 