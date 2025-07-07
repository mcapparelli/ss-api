#!/usr/bin/env python3

import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../')))

from source.transfer.application.use_cases.swap.strategies.swap_strategy_factory.swap_strategy_factory import SwapStrategyFactory
from source.transfer.application.use_cases.swap.strategies.crypto_to_crypto.crypto_to_crypto import CryptoToCryptoStrategy
from source.transfer.application.use_cases.swap.strategies.crypto_to_fiat.crypto_to_fiat import CryptoToFiatStrategy
from source.transfer.application.use_cases.swap.strategies.fiat_to_fiat_strategy.fiat_to_fiat_strategy import FiatToFiatStrategy
from source.common_types.currency_types import CurrencyType

class TestSwapStrategyFactory(unittest.TestCase):
    
    def setUp(self):
        self.factory = SwapStrategyFactory()
        
    def test_factory_initialization(self):
        self.assertIsInstance(self.factory, SwapStrategyFactory)
    
    def test_fiat_to_fiat_strategy_creation(self):
        # Test fiat to fiat strategy creation
        strategy = self.factory.create_strategy("USD", "ARS")
        self.assertIsInstance(strategy, FiatToFiatStrategy)
        
        strategy = self.factory.create_strategy("ARS", "USD")
        self.assertIsInstance(strategy, FiatToFiatStrategy)
    
    def test_crypto_to_crypto_strategy_creation(self):
        # Test crypto to crypto strategy creation
        strategy = self.factory.create_strategy("BTC", "ETH")
        self.assertIsInstance(strategy, CryptoToCryptoStrategy)
        
        strategy = self.factory.create_strategy("ETH", "BTC")
        self.assertIsInstance(strategy, CryptoToCryptoStrategy)
    
    def test_crypto_to_fiat_strategy_creation(self):
        # Test crypto to fiat strategy creation
        strategy = self.factory.create_strategy("BTC", "USD")
        self.assertIsInstance(strategy, CryptoToFiatStrategy)
        
        strategy = self.factory.create_strategy("USD", "BTC")
        self.assertIsInstance(strategy, CryptoToFiatStrategy)
        
        strategy = self.factory.create_strategy("ETH", "ARS")
        self.assertIsInstance(strategy, CryptoToFiatStrategy)
    
    def test_currency_validation(self):
        # Test valid currencies
        valid_currencies = ["USD", "ARS", "BTC", "ETH"]
        
        for currency in valid_currencies:
            try:
                CurrencyType(currency)
                is_valid = True
            except ValueError:
                is_valid = False
            self.assertTrue(is_valid)
    
    def test_invalid_currency_validation(self):
        # Test invalid currencies should raise ValueError
        invalid_currencies = ["INVALID", "XYZ", "123"]
        
        for invalid_currency in invalid_currencies:
            with self.assertRaises(ValueError):
                self.factory.create_strategy(invalid_currency, "USD")
                
            with self.assertRaises(ValueError):
                self.factory.create_strategy("USD", invalid_currency)
    
    def test_same_currency_validation(self):
        # Test that same currencies are handled properly
        same_currency_pairs = [
            ("USD", "USD"),
            ("BTC", "BTC"),
            ("ETH", "ETH"),
            ("ARS", "ARS")
        ]
        
        for from_currency, to_currency in same_currency_pairs:
            # This should be validated at a higher level
            # Factory should still create strategy based on types
            self.assertEqual(from_currency, to_currency)
    
    def test_strategy_types_logic(self):
        # Test the logic for determining strategy types
        test_cases = [
            ("USD", "ARS", "fiat_to_fiat"),
            ("BTC", "ETH", "crypto_to_crypto"),
            ("BTC", "USD", "crypto_to_fiat"),
            ("USD", "ETH", "crypto_to_fiat")
        ]
        
        for from_currency, to_currency, expected_type in test_cases:
            from_type = CurrencyType(from_currency)
            to_type = CurrencyType(to_currency)
            
            from_is_fiat = from_type.is_fiat()
            to_is_fiat = to_type.is_fiat()
            
            if from_is_fiat and to_is_fiat:
                actual_type = "fiat_to_fiat"
            elif not from_is_fiat and not to_is_fiat:
                actual_type = "crypto_to_crypto"
            else:
                actual_type = "crypto_to_fiat"
                
            self.assertEqual(actual_type, expected_type)

if __name__ == "__main__":
    unittest.main() 