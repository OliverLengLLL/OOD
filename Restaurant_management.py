from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import uuid

# Enums
class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"

class TableStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    DIGITAL = "digital"

class StaffRole(Enum):
    WAITER = "waiter"
    CHEF = "chef"
    MANAGER = "manager"

# Base Classes
class Person:
    def __init__(self, person_id: str, name: str, phone: str):
        self.id = person_id
        self.name = name
        self.phone = phone

# Menu System
class MenuItem:
    def __init__(self, item_id: str, name: str, price: float, category: str, description: str = ""):
        self.id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.available = True
    
    def __str__(self):
        return f"{self.name} - ${self.price} ({self.category})"

class Menu:
    def __init__(self):
        self.items: Dict[str, MenuItem] = {}
        self.categories: Dict[str, List[MenuItem]] = {}
    
    def add_item(self, item: MenuItem):
        self.items[item.id] = item
        if item.category not in self.categories:
            self.categories[item.category] = []
        self.categories[item.category].append(item)
    
    def remove_item(self, item_id: str):
        if item_id in self.items:
            item = self.items[item_id]
            self.categories[item.category].remove(item)
            del self.items[item_id]
    
    def get_item(self, item_id: str) -> Optional[MenuItem]:
        return self.items.get(item_id)
    
    def get_available_items(self) -> List[MenuItem]:
        return [item for item in self.items.values() if item.available]

# Order System
class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int, special_instructions: str = ""):
        self.menu_item = menu_item
        self.quantity = quantity
        self.special_instructions = special_instructions
        self.subtotal = menu_item.price * quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} - ${self.subtotal}"

class Order:
    def __init__(self, order_id: str, table_number: int, customer: 'Customer'):
        self.id = order_id
        self.table_number = table_number
        self.customer = customer
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.total_amount = 0.0
        self.special_requests = ""
    
    def add_item(self, menu_item: MenuItem, quantity: int, special_instructions: str = ""):
        order_item = OrderItem(menu_item, quantity, special_instructions)
        self.items.append(order_item)
        self.calculate_total()
    
    def remove_item(self, item_index: int):
        if 0 <= item_index < len(self.items):
            self.items.pop(item_index)
            self.calculate_total()
    
    def calculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items)
    
    def update_status(self, status: OrderStatus):
        self.status = status
        print(f"Order {self.id} status updated to: {status.value}")
    
    def __str__(self):
        items_str = "\n".join([str(item) for item in self.items])
        return f"Order {self.id} - Table {self.table_number}\n{items_str}\nTotal: ${self.total_amount}"

# Customer and Table Management
class Customer(Person):
    def __init__(self, customer_id: str, name: str, phone: str, email: str = ""):
        super().__init__(customer_id, name, phone)
        self.email = email
        self.order_history: List[Order] = []

class Table:
    def __init__(self, table_number: int, capacity: int):
        self.number = table_number
        self.capacity = capacity
        self.status = TableStatus.AVAILABLE
        self.current_order: Optional[Order] = None
    
    def occupy(self, order: Order):
        self.status = TableStatus.OCCUPIED
        self.current_order = order
    
    def free(self):
        self.status = TableStatus.AVAILABLE
        self.current_order = None

# Staff Management
class Staff(Person):
    def __init__(self, staff_id: str, name: str, phone: str, role: StaffRole):
        super().__init__(staff_id, name, phone)
        self.role = role
        self.is_available = True

class Waiter(Staff):
    def __init__(self, staff_id: str, name: str, phone: str):
        super().__init__(staff_id, name, phone, StaffRole.WAITER)
        self.assigned_tables: List[int] = []
    
    def take_order(self, table: Table, customer: Customer, menu: Menu) -> Order:
        order_id = str(uuid.uuid4())[:8]
        order = Order(order_id, table.number, customer)
        table.occupy(order)
        return order
    
    def serve_order(self, order: Order):
        order.update_status(OrderStatus.SERVED)

class Chef(Staff):
    def __init__(self, staff_id: str, name: str, phone: str):
        super().__init__(staff_id, name, phone, StaffRole.CHEF)
    
    def prepare_order(self, order: Order):
        order.update_status(OrderStatus.PREPARING)
        # Simulate preparation time
        print(f"Chef {self.name} is preparing order {order.id}")
        order.update_status(OrderStatus.READY)

# Payment System
class Payment(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CashPayment(Payment):
    def __init__(self, amount_received: float):
        self.amount_received = amount_received
    
    def process_payment(self, amount: float) -> bool:
        if self.amount_received >= amount:
            self.change = self.amount_received - amount
            return True
        return False

class CardPayment(Payment):
    def __init__(self, card_number: str):
        self.card_number = card_number
    
    def process_payment(self, amount: float) -> bool:
        # Simulate card processing
        print(f"Processing card payment of ${amount}")
        return True

class Bill:
    def __init__(self, bill_id: str, order: Order):
        self.id = bill_id
        self.order = order
        self.subtotal = order.total_amount
        self.tax_rate = 0.08  # 8% tax
        self.tax_amount = self.subtotal * self.tax_rate
        self.tip_amount = 0.0
        self.total_amount = self.subtotal + self.tax_amount
        self.created_at = datetime.now()
        self.is_paid = False
    
    def add_tip(self, tip_amount: float):
        self.tip_amount = tip_amount
        self.total_amount = self.subtotal + self.tax_amount + self.tip_amount
    
    def pay(self, payment: Payment) -> bool:
        if payment.process_payment(self.total_amount):
            self.is_paid = True
            return True
        return False
    
    def __str__(self):
        return f"""
Bill {self.id}
{self.order}
Subtotal: ${self.subtotal:.2f}
Tax: ${self.tax_amount:.2f}
Tip: ${self.tip_amount:.2f}
Total: ${self.total_amount:.2f}
"""

# Main Restaurant System
class Restaurant:
    def __init__(self, name: str):
        self.name = name
        self.menu = Menu()
        self.tables: Dict[int, Table] = {}
        self.staff: Dict[str, Staff] = {}
        self.orders: Dict[str, Order] = {}
        self.bills: Dict[str, Bill] = {}
        self.customers: Dict[str, Customer] = {}
    
    def add_table(self, table_number: int, capacity: int):
        self.tables[table_number] = Table(table_number, capacity)
    
    def add_staff(self, staff: Staff):
        self.staff[staff.id] = staff
    
    def add_customer(self, customer: Customer):
        self.customers[customer.id] = customer
    
    def get_available_tables(self) -> List[Table]:
        return [table for table in self.tables.values() if table.status == TableStatus.AVAILABLE]
    
    def create_order(self, table_number: int, customer: Customer, waiter: Waiter) -> Order:
        if table_number not in self.tables:
            raise ValueError("Table not found")
        
        table = self.tables[table_number]
        if table.status != TableStatus.AVAILABLE:
            raise ValueError("Table is not available")
        
        order = waiter.take_order(table, customer, self.menu)
        self.orders[order.id] = order
        return order
    
    def generate_bill(self, order_id: str) -> Bill:
        if order_id not in self.orders:
            raise ValueError("Order not found")
        
        order = self.orders[order_id]
        bill_id = str(uuid.uuid4())[:8]
        bill = Bill(bill_id, order)
        self.bills[bill_id] = bill
        return bill
    
    def complete_order(self, order_id: str, payment: Payment) -> bool:
        bill = self.generate_bill(order_id)
        if bill.pay(payment):
            order = self.orders[order_id]
            # Free the table
            for table in self.tables.values():
                if table.current_order and table.current_order.id == order_id:
                    table.free()
                    break
            return True
        return False

# Demo Usage
def demo_restaurant_system():
    # Create restaurant
    restaurant = Restaurant("The Good Fork")
    
    # Add tables
    for i in range(1, 6):
        restaurant.add_table(i, 4)  # 5 tables with 4 seats each
    
    # Create staff
    waiter1 = Waiter("W001", "Alice Johnson", "555-0101")
    chef1 = Chef("C001", "Bob Wilson", "555-0102")
    restaurant.add_staff(waiter1)
    restaurant.add_staff(chef1)
    
    # Create menu items
    appetizer1 = MenuItem("A001", "Caesar Salad", 12.99, "Appetizer")
    main1 = MenuItem("M001", "Grilled Salmon", 24.99, "Main Course")
    dessert1 = MenuItem("D001", "Chocolate Cake", 8.99, "Dessert")
    
    restaurant.menu.add_item(appetizer1)
    restaurant.menu.add_item(main1)
    restaurant.menu.add_item(dessert1)
    
    # Create customer
    customer1 = Customer("CUST001", "John Doe", "555-0201", "john@email.com")
    restaurant.add_customer(customer1)
    
    print("=== Restaurant Management System Demo ===")
    print(f"Restaurant: {restaurant.name}")
    print(f"Available tables: {len(restaurant.get_available_tables())}")
    print()
    
    # Create an order
    order = restaurant.create_order(1, customer1, waiter1)
    print(f"Created order: {order.id} for table 1")
    
    # Add items to order
    order.add_item(appetizer1, 1)
    order.add_item(main1, 2)
    order.add_item(dessert1, 1)
    
    print("Order details:")
    print(order)
    print()
    
    # Chef prepares the order
    chef1.prepare_order(order)
    
    # Waiter serves the order
    waiter1.serve_order(order)
    print()
    
    # Generate bill and process payment
    bill = restaurant.generate_bill(order.id)
    bill.add_tip(5.00)  # Add $5 tip
    
    print("Bill:")
    print(bill)
    
    # Process payment
    payment = CardPayment("1234-5678-9012-3456")
    if restaurant.complete_order(order.id, payment):
        print("Payment successful! Order completed.")
    else:
        print("Payment failed!")
    
    print(f"Available tables after order completion: {len(restaurant.get_available_tables())}")

if __name__ == "__main__":
    demo_restaurant_system()