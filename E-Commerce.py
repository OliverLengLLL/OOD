class Address:
  def __init__(self, zip_code, address, city, state, country):
    self.__zip_code = zip_code
    self.__address = address
    self.__city = city
    self.__state = state
    self.__country = country

class OrderStatus(enum.Enum):
  UNSHIPPED = 1 
  PENDING = 2
  SHIPPED = 3
  CONFIRMED = 4
  CANCELED = 5
  REFUNDED = 6

class AccountStatus(enum.Enum):
  ACTIVE = 1 
  INACTIVE = 2
  BLOCKED = 3

class ShipmentStatus(enum.Enum):
  PENDING = 1 
  SHIPPED = 2
  DELIVERED = 3
  ON_HOLD = 4

class PaymentStatus(enum.Enum):
  CONFIRMED = 1 
  DECLINED = 2
  PENDING = 3
  REFUNDED = 4

class Account:
  def __init__(self, user_name, password, name, shipping_address, status, email, phone, credit_cards, bank_accounts):
    self.__user_name = user_name
    self.__password = password
    self.__name = name
    self.__shipping_address = shipping_address # List of shipping addresses
    self.__status = status # Refers to the AccountStatus enum
    self.__email = email
    self.__phone = phone
    self.__credit_cards = credit_cards # List of credit cards
    self.__bank_accounts = bank_accounts # List of bank accounts

  # Returns list of shipping addresses
  def get_shipping_address(self):
    pass

  # product here refers to an instance of the Product class
  def add_product(self, product):
    pass 

  # review here refers to an instance of the ProductReview class
  # product here refers to an instance of the Product class
  def add_product_review(self, review, product):
    pass  

  # product here refers to an instance of the Product class
  def delete_product(self, product):
    pass 

  # review here refers to an instance of the ProductReview class
  # product here refers to an instance of the Product class
  def delete_product_review(self, review, product):
    pass  

  def reset_password(self):
    pass 
  
class Admin:
  def __init__(self, account):
    self.__account = account # Refers to an instance of the Account class

  # account here refers to an instance of the Account class
  def block_user(self, account):
    pass

  # category here refers to an instance of the ProductCategory class
  def add_new_product_category(self, category):
    pass

  # category here refers to an instance of the ProductCategory class
  def modify_product_category(self, category):
    pass

  # category here refers to an instance of the ProductCategory class
  def delete_product_category(self, category):
    pass
  
# Customer is an abstract class
from abc import ABC, abstractmethod

class Customer(ABC):
  def __init__(self, cart, order):
    self.__cart = cart # Refers to an instance of the ShoppingCart class

  # Returns the ShoppingCart class
  @abstractmethod
  def get_shopping_cart(self):
    pass

class Guest(Customer):
  def __init__(self, cart, order):
    super().__init__(cart, order)

  def register_account(self):
    pass

  # Returns the ShoppingCart class
  def get_shopping_cart(self):
    # Add functionality
    pass

class AuthenticatedUser(Customer):
  def __init__(self, account, cart, order):
    self.__account = account # Refers to an instance of the Account class
    self.__order = order # Refers to an instance of the Order class
    super().__init__(cart, order)

  # order here refers to an instance of the Order class
  # Returns a value from the OrderStatus enum
  def place_order(self, order):
    pass

  # Returns the ShopppingCart class
  def get_shopping_cart(self):
    # Add functionality
    pass
  
class Product:
  def __init__(self, product_id, name, description, image, price, category, reviews, available_item_count, account):
    self.__product_id = product_id
    self.__name = name
    self.__description = description
    self.__image = image
    self.__price = price
    self.__category = category # Refers to an instance of the ProductCategory class
    self.__reviews = reviews # Refers to the list of the ProductReview instances
    self.__available_item_count = available_item_count
    self.__account = account # Refers to an instance of the Account class

  def get_available_count(self):
    pass
  def update_available_count(self):
    pass
  def update_price(self, new_price):
    pass

class ProductCategory:
  def __init__(self, name, description, products):
    self.__name = name
    self.__description = description
    self.__products = products # Refers to the list of products

class ProductReview:
  def __init__(self, rating, review, image, user):
    self.__rating = rating
    self.__review = review
    self.__image = image
    self.__user = user # Refers to an instance of the AuthenticatedUser class


class CartItem:
  def __init__(self, quantity, price):
    self.__quantity = quantity
    self.__price = price
  
  def update_quantity(self, quantity):
    pass

class ShoppingCart:
  def __init__(self, total_price, items):
    self.__total_price = total_price
    self.__items = items # List of items

  # item here refers to an instance of the Item class
  def add_item(self, item):
    pass
  # item here refers to an instance of the Item class
  def remove_item(self, item):
    pass
  def get_items(self): # Returns list of items
    pass 
  def checkout(self):
    pass
  
class Order:
  def __init__(self, order_number, status, order_date, order_log, shopping_cart):
    self.__order_number = order_number
    self.__status = status # Refers to the OrderStatus enum
    self.__order_date = order_date
    self.__order_log = order_log # List of order logs
    self.__shopping_cart = shopping_cart

  def send_for_shipment(self):
    pass
  # payment here refers to an instance of the Payment class
  def make_payment(self, payment):
    pass
  # order_log here refers to an instance of the OrderLog class
  def add_order_log(self, order_log):
    pass

class OrderLog:
  def __init__(self, order_number, creation_date, status):
    self.__order_number = order_number
    self.__creation_date = creation_date
    self.__status = status # Refers to the OrderStatus enum

class Shipment:
  def __init__(self, shipment_number, shipment_date, estimated_arrival, shipment_method, shipment_logs):
    self.__shipment_number = shipment_number
    self.__shipment_date = shipment_date
    self.__estimated_arrival = estimated_arrival
    self.__shipment_method = shipment_method
    self.__shipment_logs = shipment_logs # List of shipment logs

  # shipment_log here refers to an instance of the ShipmentLog class
  def add_shipment_log(self, shipment_log):
    pass

class ShipmentLog:
  def __init__(self, shipment_number, creation_date, status):
    self.__shipment_number = shipment_number
    self.__creation_date = creation_date
    self.__status = status # Refers to the ShipmentStatus enum

# Payment is an abstract class
from abc import ABC, abstractmethod

class Payment(ABC):
  def __init__(self, amount, timestamp, status):
    self.__amount = amount
    self.__timestamp = timestamp
    self.__status = status # Refers to the PaymentStatus enum

  # Returns the PaymentStatus enum
  @abstractmethod
  def make_payment(self):
    pass

class CreditCard(Payment):
  def __init__(self, amount, timestamp, status, name_on_card, card_number, billing_address, code):
    self.__name_on_card = name_on_card
    self.__card_number = card_number
    self.__billing_address = billing_address
    self.__code = code
    super().__init__(amount, timestamp, status)

  # Returns the PaymentStatus enum
  def make_payment(self):
    # functionality
    pass

class ElectronicBankTransfer(Payment):
  def __init__(self, amount, timestamp, status, bank_name, routing_number, account_number, billing_address):
    self.__bank_name = bank_name
    self.__account_number = routing_number
    self.__account_number = account_number
    self.__billing_address = billing_address
    super().__init__(amount, timestamp, status)
  
  # Returns the PaymentStatus enum
  def make_payment(self):
    # functionality
    pass

class Cash(Payment):
  def __init__(self, amount, timestamp, status, billing_address):
    self.__billing_address = billing_address
    super().__init__(amount, timestamp, status)

  # Returns the PaymentStatus enum
  def make_payment(self):
    # functionality
    pass