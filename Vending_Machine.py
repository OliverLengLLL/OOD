
from abc import ABC, abstractmethod
from enum import Enum
from decimal import Decimal
from typing import Dict, List, Optional
import time

# Enums for better type safety
class ProductType(Enum):
    SNACK = "snack"
    DRINK = "drink"
    CANDY = "candy"

class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"

class TransactionStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Core Product class
class Product:
    def __init__(self, id: str, name: str, price: Decimal, product_type: ProductType):
        self.id = id
        self.name = name
        self.price = price
        self.product_type = product_type
    
    def __str__(self):
        return f"{self.name} (${self.price})"

# Inventory management
class InventorySlot:
    def __init__(self, product: Product, quantity: int = 0, max_capacity: int = 10):
        self.product = product
        self.quantity = quantity
        self.max_capacity = max_capacity
    
    def is_available(self) -> bool:
        return self.quantity > 0
    
    def can_restock(self, amount: int) -> bool:
        return self.quantity + amount <= self.max_capacity
    
    def restock(self, amount: int) -> bool:
        if self.can_restock(amount):
            self.quantity += amount
            return True
        return False
    
    def dispense(self) -> bool:
        if self.is_available():
            self.quantity -= 1
            return True
        return False

class Inventory:
    def __init__(self):
        self.slots: Dict[str, InventorySlot] = {}
    
    def add_product_slot(self, slot_id: str, product: Product, quantity: int = 0):
        self.slots[slot_id] = InventorySlot(product, quantity)
    
    def get_slot(self, slot_id: str) -> Optional[InventorySlot]:
        return self.slots.get(slot_id)
    
    def is_product_available(self, slot_id: str) -> bool:
        slot = self.get_slot(slot_id)
        return slot is not None and slot.is_available()
    
    def get_available_products(self) -> Dict[str, InventorySlot]:
        return {slot_id: slot for slot_id, slot in self.slots.items() if slot.is_available()}

# Abstract Payment interface
class Payment(ABC):
    def __init__(self, amount: Decimal):
        self.amount = amount
        self.timestamp = time.time()
    
    @abstractmethod
    def process_payment(self) -> bool:
        pass
    
    @abstractmethod
    def get_payment_method(self) -> PaymentMethod:
        pass

class CashPayment(Payment):
    def __init__(self, amount: Decimal, cash_inserted: Decimal):
        super().__init__(amount)
        self.cash_inserted = cash_inserted
    
    def process_payment(self) -> bool:
        return self.cash_inserted >= self.amount
    
    def get_change(self) -> Decimal:
        if self.cash_inserted >= self.amount:
            return self.cash_inserted - self.amount
        return Decimal('0')
    
    def get_payment_method(self) -> PaymentMethod:
        return PaymentMethod.CASH

class CardPayment(Payment):
    def __init__(self, amount: Decimal, card_number: str):
        super().__init__(amount)
        self.card_number = card_number
    
    def process_payment(self) -> bool:
        # Simulate card processing
        return len(self.card_number) >= 10  # Basic validation
    
    def get_payment_method(self) -> PaymentMethod:
        return PaymentMethod.CARD

# Transaction handling
class Transaction:
    def __init__(self, slot_id: str, product: Product, payment: Payment):
        self.slot_id = slot_id
        self.product = product
        self.payment = payment
        self.status = TransactionStatus.PENDING
        self.timestamp = time.time()
        self.change_due = Decimal('0')
    
    def process(self) -> bool:
        if self.payment.process_payment():
            self.status = TransactionStatus.SUCCESS
            if isinstance(self.payment, CashPayment):
                self.change_due = self.payment.get_change()
            return True
        else:
            self.status = TransactionStatus.FAILED
            return False
    
    def cancel(self):
        self.status = TransactionStatus.CANCELLED

# Display system
class Display:
    def __init__(self):
        self.message = "Welcome! Please select a product."
    
    def show_products(self, available_products: Dict[str, InventorySlot]):
        product_list = []
        for slot_id, slot in available_products.items():
            product_list.append(f"{slot_id}: {slot.product} (Qty: {slot.quantity})")
        return "\n".join(product_list)
    
    def show_message(self, message: str):
        self.message = message
        print(f"DISPLAY: {message}")
    
    def show_transaction_result(self, transaction: Transaction):
        if transaction.status == TransactionStatus.SUCCESS:
            msg = f"Success! Dispensed {transaction.product.name}"
            if transaction.change_due > 0:
                msg += f". Change: ${transaction.change_due}"
        elif transaction.status == TransactionStatus.FAILED:
            msg = "Payment failed. Please try again."
        else:
            msg = "Transaction cancelled."
        self.show_message(msg)

# Main Vending Machine class
class VendingMachine:
    def __init__(self):
        self.inventory = Inventory()
        self.display = Display()
        self.cash_balance = Decimal('100.00')  # Starting change available
        self.transactions: List[Transaction] = []
    
    def add_product(self, slot_id: str, product: Product, quantity: int = 5):
        self.inventory.add_product_slot(slot_id, product, quantity)
    
    def select_product(self, slot_id: str) -> Optional[Product]:
        if self.inventory.is_product_available(slot_id):
            slot = self.inventory.get_slot(slot_id)
            return slot.product
        else:
            self.display.show_message(f"Product {slot_id} not available")
            return None
    
    def insert_cash(self, slot_id: str, cash_amount: Decimal) -> Optional[Transaction]:
        product = self.select_product(slot_id)
        if not product:
            return None
        
        payment = CashPayment(product.price, cash_amount)
        transaction = Transaction(slot_id, product, payment)
        
        if self._process_transaction(transaction):
            return transaction
        return None
    
    def pay_with_card(self, slot_id: str, card_number: str) -> Optional[Transaction]:
        product = self.select_product(slot_id)
        if not product:
            return None
        
        payment = CardPayment(product.price, card_number)
        transaction = Transaction(slot_id, product, payment)
        
        if self._process_transaction(transaction):
            return transaction
        return None
    
    def _process_transaction(self, transaction: Transaction) -> bool:
        # Process payment
        if not transaction.process():
            self.display.show_transaction_result(transaction)
            return False
        
        # Check if we can make change (for cash payments)
        if isinstance(transaction.payment, CashPayment):
            if transaction.change_due > self.cash_balance:
                transaction.status = TransactionStatus.FAILED
                self.display.show_message("Exact change required")
                return False
        
        # Dispense product
        slot = self.inventory.get_slot(transaction.slot_id)
        if slot and slot.dispense():
            # Update cash balance
            if isinstance(transaction.payment, CashPayment):
                self.cash_balance += transaction.payment.amount
                self.cash_balance -= transaction.change_due
            
            self.transactions.append(transaction)
            self.display.show_transaction_result(transaction)
            return True
        else:
            transaction.status = TransactionStatus.FAILED
            self.display.show_message("Dispensing failed")
            return False
    
    def restock(self, slot_id: str, quantity: int) -> bool:
        slot = self.inventory.get_slot(slot_id)
        if slot:
            return slot.restock(quantity)
        return False
    
    def show_available_products(self):
        available = self.inventory.get_available_products()
        if available:
            products = self.display.show_products(available)
            print("Available Products:")
            print(products)
        else:
            self.display.show_message("No products available")
    
    def get_sales_report(self) -> Dict:
        successful_transactions = [t for t in self.transactions if t.status == TransactionStatus.SUCCESS]
        total_revenue = sum(t.product.price for t in successful_transactions)
        
        return {
            "total_transactions": len(successful_transactions),
            "total_revenue": total_revenue,
            "cash_balance": self.cash_balance,
            "products_sold": len(successful_transactions)
        }