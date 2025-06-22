from datetime import datetime
from typing import List, Optional
from uuid import uuid4

# Product classes
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name}: ${self.price:.2f}"


class Pizza(Product):
    def __init__(self, name: str, size: str, price: float):
        self.size = size  # small, medium, large
        super().__init__(f"{size.capitalize()} {name} Pizza", price)


class Drink(Product):
    def __init__(self, name: str, size: str, price: float):
        self.size = size  # small, medium, large
        super().__init__(f"{size.capitalize()} {name}", price)


class Snack(Product):
    def __init__(self, name: str, price: float):
        super().__init__(name, price)


# Customer class
class Customer:
    def __init__(self, name: str, phone: str, address: str):
        self.name = name
        self.phone = phone
        self.address = address


# Order class with simple discount support
class Order:
    def __init__(self, customer: Customer, items: List[Product]):
        self.order_id = str(uuid4())[:8]  # Shorter ID for simplicity
        self.customer = customer
        self.items = items
        self.subtotal = sum(item.price for item in items)
        self.discount = 0.0
        self.total = self.subtotal
        self.status = "Received"
        self.order_time = datetime.now()

    def add_item(self, item: Product):
        self.items.append(item)
        self.subtotal += item.price
        self.total = self.subtotal - self.discount

    def apply_fixed_discount(self, amount: float) -> bool:
        """Apply a fixed amount discount (e.g., $10 off)"""
        if amount <= 0:
            return False

        # Can't discount more than the total
        self.discount = min(amount, self.subtotal)
        self.total = self.subtotal - self.discount
        return True

    def apply_percentage_discount(self, percentage: float) -> bool:
        """Apply a percentage discount (e.g., 20% off)"""
        if percentage <= 0 or percentage > 100:
            return False

        self.discount = self.subtotal * (percentage / 100)
        self.total = self.subtotal - self.discount
        return True

    def update_status(self, new_status: str):
        self.status = new_status

    def get_receipt(self) -> str:
        """Generate a simple receipt"""
        receipt = f"\n===== ORDER #{self.order_id} =====\n"
        receipt += f"Customer: {self.customer.name}\n"
        receipt += f"Time: {self.order_time.strftime('%Y-%m-%d %H:%M')}\n"
        receipt += f"Status: {self.status}\n"
        receipt += "---------------------------\n"

        for item in self.items:
            receipt += f"{item}\n"

        receipt += "---------------------------\n"
        receipt += f"Subtotal: ${self.subtotal:.2f}\n"

        if self.discount > 0:
            receipt += f"Discount: -${self.discount:.2f}\n"

        receipt += f"TOTAL: ${self.total:.2f}\n"
        receipt += "===========================\n"

        return receipt


# Simple coupon class
class Coupon:
    def __init__(self, code: str, is_percentage: bool, value: float):
        self.code = code.upper()
        self.is_percentage = is_percentage  # True if percentage, False if fixed amount
        self.value = value  # Percentage or dollar amount

    def apply_to_order(self, order: Order) -> bool:
        """Apply the coupon to an order"""
        if self.is_percentage:
            return order.apply_percentage_discount(self.value)
        else:
            return order.apply_fixed_discount(self.value)


# Pizza Store class
class PizzaStore:
    def __init__(self, name: str):
        self.name = name
        self.active_orders = []
        self.available_coupons = {}  # code -> Coupon
        self.setup_coupons()

    def setup_coupons(self):
        """Initialize available coupons"""
        self.available_coupons = {
            "FLAT10": Coupon("FLAT10", False, 10.0),  # $10 off
            "HALF": Coupon("HALF", True, 50.0),  # 50% off
            "SAVE20": Coupon("SAVE20", True, 20.0),  # 20% off
            "SAVE5": Coupon("SAVE5", False, 5.0)  # $5 off
        }

    def get_menu(self) -> dict:
        """Return a simple menu with prices"""
        return {
            "Pizzas": {
                "Small Cheese Pizza": 8.99,
                "Medium Cheese Pizza": 10.99,
                "Large Cheese Pizza": 12.99,
                "Small Pepperoni Pizza": 9.99,
                "Medium Pepperoni Pizza": 11.99,
                "Large Pepperoni Pizza": 13.99,
                "Small Vegetarian Pizza": 10.99,
                "Medium Vegetarian Pizza": 12.99,
                "Large Vegetarian Pizza": 14.99,
            },
            "Drinks": {
                "Small Soda": 1.99,
                "Medium Soda": 2.49,
                "Large Soda": 2.99,
                "Bottled Water": 1.50,
            },
            "Snacks": {
                "Breadsticks": 3.99,
                "Cheese Breadsticks": 4.99,
                "Wings (6 pcs)": 5.99,
                "Side Salad": 3.99,
            }
        }

    def print_menu(self):
        """Print the menu"""
        menu = self.get_menu()
        print(f"\n===== {self.name} MENU =====")

        for category, items in menu.items():
            print(f"\n{category}:")
            for item, price in items.items():
                print(f"  {item}: ${price:.2f}")

        print("\n=======================")

    def print_coupons(self):
        """Print available coupons"""
        print(f"\n===== {self.name} COUPONS =====")

        for code, coupon in self.available_coupons.items():
            if coupon.is_percentage:
                print(f"  {code}: {coupon.value}% off your order")
            else:
                print(f"  {code}: ${coupon.value:.2f} off your order")

        print("\n=======================")

    def place_order(self, customer: Customer, items: List[Product], coupon_code: Optional[str] = None) -> Order:
        """Create a new order with optional coupon"""
        order = Order(customer, items)

        # Apply coupon if provided
        if coupon_code:
            coupon = self.available_coupons.get(coupon_code.upper())
            if coupon:
                if coupon.apply_to_order(order):
                    print(f"Coupon {coupon_code} applied successfully!")
                else:
                    print(f"Coupon {coupon_code} could not be applied.")
            else:
                print(f"Invalid coupon code: {coupon_code}")

        self.active_orders.append(order)
        order.update_status("Preparing")
        return order

    def update_order_status(self, order_id: str, new_status: str):
        """Update the status of an order"""
        for order in self.active_orders:
            if order.order_id == order_id:
                order.update_status(new_status)
                print(f"Order {order_id} updated to: {new_status}")
                if new_status == "Delivered":
                    self.active_orders.remove(order)
                break


def main():
    store = PizzaStore("Pizza Paradise")
    store.print_menu()
    store.print_coupons()

    customer = Customer("John Doe", "123-456-7890", "123 Elm St")
    items = [
        Pizza("Cheese", "medium", 10.99),
        Drink("Soda", "large", 2.99),
        Snack("Breadsticks", 3.99)          
    ]
    order = store.place_order(customer, items, coupon_code="FLAT10")
    print(order.get_receipt())  

    store.update_order_status(order.order_id, "Delivered")
    print(f"Order {order.order_id} has been delivered.")
    

if __name__ == "__main__":
    main()