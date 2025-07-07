#!/usr/bin/env python3

import sys
import os
import unittest
import uuid
from decimal import Decimal

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

# Importar las entidades para que SQLAlchemy las reconozca
from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.common_types import CurrencyType

class TestUserBalanceEntity(unittest.TestCase):
    
    def setUp(self):
        self.user_id = uuid.uuid4()
        self.currency = CurrencyType.USD
        self.initial_amount = 1000.0
        
        self.balance = UserBalance(
            id=1,
            user_id=self.user_id,
            currency=self.currency,
            amount=Decimal(str(self.initial_amount))
        )
    
    def test_increment_positive_amount(self):
        initial_amount = self.balance.amount
        increment_amount = 500.0
        
        self.balance.increment(increment_amount)
        
        expected_amount = initial_amount + Decimal(str(increment_amount))
        self.assertEqual(self.balance.amount, expected_amount)
    
    def test_increment_zero_amount(self):
        initial_amount = self.balance.amount
        
        self.balance.increment(0.0)
        
        self.assertEqual(self.balance.amount, initial_amount)
    
    def test_increment_negative_amount(self):
        with self.assertRaises(ValueError) as context:
            self.balance.increment(-100.0)
        
        self.assertIn("Amount to increment must be positive", str(context.exception))
    
    def test_increment_invalid_amount(self):
        with self.assertRaises(ValueError) as context:
            self.balance.increment("invalid")
        
        self.assertIn("Error incrementing balance", str(context.exception))
    
    def test_decrement_positive_amount(self):
        initial_amount = self.balance.amount
        decrement_amount = 200.0
        
        self.balance.decrement(decrement_amount)
        
        expected_amount = initial_amount - Decimal(str(decrement_amount))
        self.assertEqual(self.balance.amount, expected_amount)
    
    def test_decrement_exact_amount(self):
        self.balance.decrement(self.initial_amount)
        self.assertEqual(self.balance.amount, Decimal('0'))
    
    def test_decrement_insufficient_amount(self):
        with self.assertRaises(ValueError) as context:
            self.balance.decrement(2000.0)
        
        self.assertIn("Insufficient balance", str(context.exception))
        self.assertIn("Available", str(context.exception))
        self.assertIn("Required", str(context.exception))
    
    def test_decrement_negative_amount(self):
        with self.assertRaises(ValueError) as context:
            self.balance.decrement(-100.0)
        
        self.assertIn("Amount to decrement must be positive", str(context.exception))
    
    def test_decrement_zero_amount(self):
        initial_amount = self.balance.amount
        
        self.balance.decrement(0.0)
        
        self.assertEqual(self.balance.amount, initial_amount)
    
    def test_decrement_invalid_amount(self):
        with self.assertRaises(ValueError) as context:
            self.balance.decrement("invalid")
        
        self.assertIn("Error decrementing balance", str(context.exception))

if __name__ == "__main__":
    unittest.main()
