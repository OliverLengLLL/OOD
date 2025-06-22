from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import uuid

# Enums
class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

# Core Entities
class Stock:
    def __init__(self, symbol: str, company_name: str, current_price: Decimal):
        self.symbol = symbol
        self.company_name = company_name
        self.current_price = current_price
        self.last_updated = datetime.now()
    
    def update_price(self, new_price: Decimal):
        self.current_price = new_price
        self.last_updated = datetime.now()

class User:
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = datetime.now()

class Account:
    def __init__(self, user: User, initial_balance: Decimal = Decimal('0')):
        self.account_id = str(uuid.uuid4())
        self.user = user
        self.balance = initial_balance
        self.created_at = datetime.now()
    
    def deposit(self, amount: Decimal) -> bool:
        if amount > 0:
            self.balance += amount
            return True
        return False
    
    def withdraw(self, amount: Decimal) -> bool:
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            return True
        return False
    
    def has_sufficient_balance(self, amount: Decimal) -> bool:
        return self.balance >= amount

class Position:
    def __init__(self, stock: Stock, quantity: int, avg_price: Decimal):
        self.stock = stock
        self.quantity = quantity
        self.avg_price = avg_price
    
    def update_position(self, quantity_change: int, price: Decimal):
        if self.quantity + quantity_change == 0:
            self.quantity = 0
            self.avg_price = Decimal('0')
        else:
            total_cost = (self.quantity * self.avg_price) + (quantity_change * price)
            self.quantity += quantity_change
            self.avg_price = total_cost / self.quantity if self.quantity > 0 else Decimal('0')

class Portfolio:
    def __init__(self, account: Account):
        self.account = account
        self.positions: Dict[str, Position] = {}  # symbol -> Position
    
    def add_position(self, stock: Stock, quantity: int, price: Decimal):
        if stock.symbol in self.positions:
            self.positions[stock.symbol].update_position(quantity, price)
        else:
            self.positions[stock.symbol] = Position(stock, quantity, price)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)
    
    def has_sufficient_shares(self, symbol: str, quantity: int) -> bool:
        position = self.positions.get(symbol)
        return position is not None and position.quantity >= quantity
    
    def get_portfolio_value(self) -> Decimal:
        total_value = Decimal('0')
        for position in self.positions.values():
            total_value += position.quantity * position.stock.current_price
        return total_value

class Order:
    def __init__(self, account: Account, stock: Stock, order_type: OrderType, 
                 side: OrderSide, quantity: int, price: Optional[Decimal] = None):
        self.order_id = str(uuid.uuid4())
        self.account = account
        self.stock = stock
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.price = price
        self.filled_quantity = 0
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_status(self, status: OrderStatus):
        self.status = status
        self.updated_at = datetime.now()
    
    def fill_order(self, quantity: int):
        self.filled_quantity += quantity
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
        self.updated_at = datetime.now()
    
    def get_remaining_quantity(self) -> int:
        return self.quantity - self.filled_quantity

class Transaction:
    def __init__(self, account: Account, transaction_type: TransactionType, 
                 amount: Decimal, stock: Optional[Stock] = None, quantity: Optional[int] = None):
        self.transaction_id = str(uuid.uuid4())
        self.account = account
        self.transaction_type = transaction_type
        self.amount = amount
        self.stock = stock
        self.quantity = quantity
        self.timestamp = datetime.now()

# Order Processing Strategy
class OrderProcessor(ABC):
    @abstractmethod
    def process_order(self, order: Order) -> bool:
        pass

class MarketOrderProcessor(OrderProcessor):
    def __init__(self, market_data_service):
        self.market_data_service = market_data_service
    
    def process_order(self, order: Order) -> bool:
        current_price = self.market_data_service.get_current_price(order.stock.symbol)
        if current_price is None:
            return False
        
        total_cost = current_price * order.quantity
        
        if order.side == OrderSide.BUY:
            if order.account.has_sufficient_balance(total_cost):
                order.account.withdraw(total_cost)
                order.fill_order(order.quantity)
                return True
        else:  # SELL
            # Check if user has sufficient shares
            return True  # Simplified - assume user has shares
        
        return False

class LimitOrderProcessor(OrderProcessor):
    def process_order(self, order: Order) -> bool:
        if order.price is None:
            return False
        
        current_price = order.stock.current_price
        
        if order.side == OrderSide.BUY and current_price <= order.price:
            total_cost = order.price * order.quantity
            if order.account.has_sufficient_balance(total_cost):
                order.account.withdraw(total_cost)
                order.fill_order(order.quantity)
                return True
        elif order.side == OrderSide.SELL and current_price >= order.price:
            order.fill_order(order.quantity)
            order.account.deposit(order.price * order.quantity)
            return True
        
        return False

# Core Services
class MarketDataService:
    def __init__(self):
        self.stocks: Dict[str, Stock] = {}
    
    def add_stock(self, stock: Stock):
        self.stocks[stock.symbol] = stock
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        return self.stocks.get(symbol)
    
    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        stock = self.stocks.get(symbol)
        return stock.current_price if stock else None
    
    def update_stock_price(self, symbol: str, new_price: Decimal):
        if symbol in self.stocks:
            self.stocks[symbol].update_price(new_price)

class OrderService:
    def __init__(self, market_data_service: MarketDataService, portfolio_service):
        self.market_data_service = market_data_service
        self.portfolio_service = portfolio_service
        self.orders: Dict[str, Order] = {}
        self.processors = {
            OrderType.MARKET: MarketOrderProcessor(market_data_service),
            OrderType.LIMIT: LimitOrderProcessor()
        }
    
    def place_order(self, account: Account, symbol: str, order_type: OrderType, 
                   side: OrderSide, quantity: int, price: Optional[Decimal] = None) -> Optional[Order]:
        stock = self.market_data_service.get_stock(symbol)
        if not stock:
            return None
        
        order = Order(account, stock, order_type, side, quantity, price)
        
        # Validate order
        if not self._validate_order(order):
            order.update_status(OrderStatus.REJECTED)
            return order
        
        # Process order
        processor = self.processors[order_type]
        if processor.process_order(order):
            # Update portfolio
            if order.status == OrderStatus.FILLED:
                quantity_change = quantity if side == OrderSide.BUY else -quantity
                execution_price = price if order_type == OrderType.LIMIT else stock.current_price
                self.portfolio_service.update_position(account, stock, quantity_change, execution_price)
        
        self.orders[order.order_id] = order
        return order
    
    def _validate_order(self, order: Order) -> bool:
        if order.quantity <= 0:
            return False
        
        if order.order_type == OrderType.LIMIT and order.price is None:
            return False
        
        if order.side == OrderSide.SELL:
            # Check if user has sufficient shares
            return self.portfolio_service.has_sufficient_shares(
                order.account, order.stock.symbol, order.quantity)
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.update_status(OrderStatus.CANCELLED)
            return True
        return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

class PortfolioService:
    def __init__(self):
        self.portfolios: Dict[str, Portfolio] = {}  # account_id -> Portfolio
    
    def create_portfolio(self, account: Account) -> Portfolio:
        portfolio = Portfolio(account)
        self.portfolios[account.account_id] = portfolio
        return portfolio
    
    def get_portfolio(self, account: Account) -> Optional[Portfolio]:
        return self.portfolios.get(account.account_id)
    
    def update_position(self, account: Account, stock: Stock, quantity_change: int, price: Decimal):
        portfolio = self.get_portfolio(account)
        if portfolio:
            portfolio.add_position(stock, quantity_change, price)
    
    def has_sufficient_shares(self, account: Account, symbol: str, quantity: int) -> bool:
        portfolio = self.get_portfolio(account)
        return portfolio.has_sufficient_shares(symbol, quantity) if portfolio else False

class TransactionService:
    def __init__(self):
        self.transactions: List[Transaction] = []
    
    def record_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
    
    def get_account_transactions(self, account: Account) -> List[Transaction]:
        return [t for t in self.transactions if t.account.account_id == account.account_id]

# Main Brokerage System
class BrokerageSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.accounts: Dict[str, Account] = {}
        self.market_data_service = MarketDataService()
        self.portfolio_service = PortfolioService()
        self.order_service = OrderService(self.market_data_service, self.portfolio_service)
        self.transaction_service = TransactionService()
    
    def create_user(self, name: str, email: str) -> User:
        user_id = str(uuid.uuid4())
        user = User(user_id, name, email)
        self.users[user_id] = user
        return user
    
    def create_account(self, user: User, initial_balance: Decimal = Decimal('0')) -> Account:
        account = Account(user, initial_balance)
        self.accounts[account.account_id] = account
        self.portfolio_service.create_portfolio(account)
        return account
    
    def deposit_funds(self, account_id: str, amount: Decimal) -> bool:
        account = self.accounts.get(account_id)
        if account and account.deposit(amount):
            transaction = Transaction(account, TransactionType.DEPOSIT, amount)
            self.transaction_service.record_transaction(transaction)
            return True
        return False
    
    def place_order(self, account_id: str, symbol: str, order_type: str, 
                   side: str, quantity: int, price: Optional[float] = None) -> Optional[Order]:
        account = self.accounts.get(account_id)
        if not account:
            return None
        
        order_type_enum = OrderType(order_type.upper())
        side_enum = OrderSide(side.upper())
        price_decimal = Decimal(str(price)) if price else None
        
        return self.order_service.place_order(account, symbol, order_type_enum, 
                                            side_enum, quantity, price_decimal)
    
    def get_portfolio(self, account_id: str) -> Optional[Portfolio]:
        account = self.accounts.get(account_id)
        return self.portfolio_service.get_portfolio(account) if account else None
    
    def add_stock_to_market(self, symbol: str, company_name: str, price: float):
        stock = Stock(symbol, company_name, Decimal(str(price)))
        self.market_data_service.add_stock(stock)

# Example Usage
if __name__ == "__main__":
    # Initialize brokerage system
    brokerage = BrokerageSystem()
    
    # Add stocks to market
    brokerage.add_stock_to_market("AAPL", "Apple Inc.", 150.00)
    brokerage.add_stock_to_market("GOOGL", "Alphabet Inc.", 2500.00)
    brokerage.add_stock_to_market("TSLA", "Tesla Inc.", 800.00)
    
    # Create user and account
    user = brokerage.create_user("John Doe", "john@example.com")
    account = brokerage.create_account(user, Decimal('10000'))
    
    print(f"Created account {account.account_id} with balance ${account.balance}")
    
    # Place a buy order
    order = brokerage.place_order(account.account_id, "AAPL", "MARKET", "BUY", 10)
    if order:
        print(f"Order {order.order_id} placed: {order.status}")
        print(f"Account balance after order: ${order.account.balance}")
    
    # Check portfolio
    portfolio = brokerage.get_portfolio(account.account_id)
    if portfolio:
        print(f"Portfolio value: ${portfolio.get_portfolio_value()}")
        for symbol, position in portfolio.positions.items():
            print(f"{symbol}: {position.quantity} shares at avg price ${position.avg_price}")