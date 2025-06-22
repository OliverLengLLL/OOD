from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# Enums for better type safety
class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    BALANCE_INQUIRY = "BALANCE_INQUIRY"
    TRANSFER = "TRANSFER"

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

class ATMStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

class Card:
    def __init__(self, card_number: str, account_number: str, expiry_date: datetime):
        self.card_number = card_number
        self.account_number = account_number
        self.expiry_date = expiry_date
        self.is_blocked = False
    
    def is_valid(self) -> bool:
        return not self.is_blocked and self.expiry_date > datetime.now()
    

class Transaction:
    def __init__(self, transaction_id: str, account_number: str, 
                 transaction_type: TransactionType, amount: float, 
                 balance_after: float, description: str = ""):
        self.transaction_id = transaction_id
        self.account_number = account_number
        self.transaction_type = transaction_type
        self.amount = amount
        self.balance_after = balance_after
        self.timestamp = datetime.now()
        self.description = description

class CashDispenser:
    def __init__(self, initial_cash: float = 50000.0):
        self.available_cash = initial_cash
        self.min_cash_threshold = 1000.0
    
    def dispense_cash(self, amount: float) -> bool:
        if self.can_dispense(amount):
            self.available_cash -= amount
            return True
        return False
    
    def can_dispense(self, amount: float) -> bool:
        return self.available_cash >= amount and amount > 0
    
    def add_cash(self, amount: float):
        self.available_cash += amount
    
    def is_low_on_cash(self) -> bool:
        return self.available_cash < self.min_cash_threshold

class Customer:
    def __init__(self, customer_id: str, name: str, phone: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.accounts: List[str] = []  # List of account numbers
        self.cards: List[Card] = []

    def add_account(self, account_number:str):
        if account_number not in self.accounts:
            self.accounts.append(account_number)

    def add_cards(self, card: Card):
        self.cards.append(card)

class Account:
    def __init__(self, account_number: str, customer_id: str, account_type: AccountType, initial_balance: float = 0.0):
        self.account_number = account_number
        self.customer_id = customer_id
        self.account_type = account_type
        self.balance = initial_balance
        self.pin = None  # Will be set separately for security
        self.is_active = True
        self.daily_withdrawal_limit = 1000.0
        self.daily_withdrawn = 0.0
        self.transaction_history: List[Transaction] = []

    def set_pin(self, pin:str):
        self.pin = pin
    
    def verify_pin(self, pin: str) -> bool:
        return self.pin == pin
    
    def can_withdraw(self, amount: float) -> bool:
        return (self.is_active and 
                self.balance >= amount and 
                self.daily_withdrawn + amount <= self.daily_withdrawal_limit)
    
    def debit(self, amount: float, description: str = "") -> Transaction:
        if not self.can_withdraw(amount):
            return None  # Simplified - return None if cannot withdraw
        
        self.balance -= amount
        self.daily_withdrawn += amount
        transaction = Transaction(
            str(uuid.uuid4()), self.account_number, 
            TransactionType.WITHDRAW, amount, self.balance, description
        )
        self.transaction_history.append(transaction)
        return transaction
    
    def credit(self, amount: float, description: str = "") -> Transaction:
        if not self.is_active:
            return None 
        
        self.balance += amount
        transaction = Transaction(
            str(uuid.uuid4()), self.account_number, 
            TransactionType.DEPOSIT, amount, self.balance, description
        )
        self.transaction_history.append(transaction)
        return transaction
    
    def get_balance(self) -> float:
        return self.balance
    
    def reset_daily_limit(self):
        # This should be called daily
        self.daily_withdrawn = 0.0


class Request(ABC):
    def __init__(self, account_number:str, amount: float=0.0):
        self.account_number = account_number
        self.amount = amount
        self.timestamp = Date.now()

class DepositRequest(Request):
    def __init__(self, account_number: str, amount: float):
        super().__init__(account_number, amount)

class WithdrawRequest(Request):
    def __init__(self, account_number: str, amount: float):
        super().__init__(account_number, amount)

class CheckBalanceRequest(Request):
    def __init__(self, account_number: str):
        super().__init__(account_number)

class AccountTransferRequest(Request):
    def __init__(self, from_account: str, to_account: str, amount: float):
        super().__init__(from_account, amount)
        self.to_account = to_account

class ATM:
    def __init__(self, atm_id, location, initial_cash: float=50000.0):
        self.atm_id = atm_id
        self.location = location
        self.status = ATMStatus.ACTIVE
        self.cash_dispenser = CashDispenser(initial_cash)
        self.current_session = None
        self.failed_attempts = 0
        self.max_failed_attempts = 3

    def is_operational(self) -> bool:
        return (self.status == ATMStatus.ACTIVE and not self.cash_dispenser.is_low_on_cash())
    
    def authenticate_card(self, card: Card, pin:str, atm_system: ATM_System) -> bool:
        if not card.is_valid:
            return False

        account = atm_system.get_account_by_card(card.card_number)
        if account and account.verify(pin):
            self.failed_attempts = 0
            self.current_session = {
                "account_number": account.account_number,
                "start_time": datetime.now()
            }
            return True
        else:
            self.failed_attempts += 1
            if self.failed_attempts > self.max_failed_attempts:
                card.is_blocked = True
            return False
        
    def end_session(self):
        self.current_session = None
        self.failed_attempts = 0

    def process_request(self, request: Request, atm_system) -> dict:
        """Process different types of requests"""
        if not self.is_operational():
            return {"success": False, "message": "ATM is currently unavailable"}
        
        # Route to appropriate handler based on request type
        if isinstance(request, DepositRequest):
            return self._handle_deposit(request, atm_system)
        elif isinstance(request, WithdrawRequest):
            return self._handle_withdrawal(request, atm_system)
        elif isinstance(request, CheckBalanceRequest):
            return self._handle_balance_inquiry(request, atm_system)
        elif isinstance(request, AccountTransferRequest):
            return self._handle_transfer(request, atm_system)
        else:
            return {"success": False, "message": "Unsupported request type"}
        
    def _handle_deposit(self, request, atm_system):
        account = atm_system.get_account(request.account_number)
        if not account:
            return {"success": False, "message": "Account not found"}
        
        transaction = account.credit(request.amount, "ATM Deposit")
        if not transaction:
            return {"success": False, "message": "Deposit failed"}
        
        return {
            "success": True,
            "message": f"Successfully deposited ${request.amount:.2f}",
            "balance": account.get_balance(),
            "transaction_id": transaction.transaction_id
        }
    
    def _handle_withdraw(self, request, atm_system):
        account = atm_system.get_account(request.account_number)
        if not account:
            return {"success": False, "message": "Account not found"}
        
        transaction = account.debit(request.amount, "ATM Withdraw")
        if not transaction:
            return {"success": False, "message": "Deposit failed"}
        
        self.cash_dispenser.dispense_cash(request.amount)

        return {
            "success": True,
            "message": f"Successfully deposited ${request.amount:.2f}",
            "balance": account.get_balance(),
            "transaction_id": transaction.transaction_id
        }
    
    def _handle_balance_inquiry(self, request: CheckBalanceRequest, atm_system) -> dict:
        """Handle balance inquiry request"""
        account = atm_system.get_account(request.account_number)
        if not account:
            return {"success": False, "message": "Account not found"}
        
        return {
            "success": True,
            "balance": account.get_balance(),
            "account_type": account.account_type.value
        }
    
    def _handle_transfer(self, request: AccountTransferRequest, atm_system) -> dict:
        """Handle account transfer request"""
        from_acc = atm_system.get_account(request.account_number)
        to_acc = atm_system.get_account(request.to_account)
        
        if not from_acc:
            return {"success": False, "message": "Source account not found"}
        if not to_acc:
            return {"success": False, "message": "Destination account not found"}
        
        # Debit from source account
        from_transaction = from_acc.debit(request.amount, f"Transfer to {request.to_account}")
        if not from_transaction:
            return {"success": False, "message": "Transfer failed - insufficient funds"}
        
        # Credit to destination account
        to_transaction = to_acc.credit(request.amount, f"Transfer from {request.account_number}")
        if not to_transaction:
            # Rollback the debit if credit fails
            from_acc.balance += request.amount
            from_acc.daily_withdrawn -= request.amount
            return {"success": False, "message": "Transfer failed - destination account issue"}
        
        return {
            "success": True,
            "message": f"Successfully transferred ${request.amount:.2f}",
            "from_balance": from_acc.get_balance(),
            "transaction_id": from_transaction.transaction_id
        }

class ATM_System:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.customers: Dict[str, Customer] = {}
        self.cards: Dict[str, Card] = {}  # card_number -> Card mapping
        self.atms: Dict[str, ATM] = {}
        self.current_atm: Optional[ATM] = None
    
    def create_customer(self, name: str, phone: str, email: str) -> Customer:
        customer_id = str(uuid.uuid4())
        customer = Customer(customer_id, name, phone, email)
        self.customers[customer_id] = customer
        return customer
    
    def create_account(self, customer_id: str, account_type: AccountType, initial_balance: float = 0.0) -> Account:
        if customer_id not in self.customers:
            return None  # Simplified - return None if customer not found
        
        account_number = f"ACC{len(self.accounts):06d}"
        account = Account(account_number, customer_id, account_type, initial_balance)
        self.accounts[account_number] = account
        
        # Link account to customer
        self.customers[customer_id].add_account(account_number)
        return account
    
    def create_card(self, account_number: str, expiry_date: datetime) -> Card:
        if account_number not in self.accounts:
            return None  # Simplified - return None if account not found
        
        card_number = f"CARD{len(self.cards):010d}"
        card = Card(card_number, account_number, expiry_date)
        self.cards[card_number] = card
        
        # Link card to customer
        account = self.accounts[account_number]
        customer = self.customers[account.customer_id]
        customer.add_card(card)
        return card
    
    def add_atm(self, location: str, initial_cash: float = 50000.0) -> ATM:
        atm_id = f"ATM{len(self.atms):04d}"
        atm = ATM(atm_id, location, initial_cash)
        self.atms[atm_id] = atm
        return atm
    
    def get_account(self, account_number: str) -> Account:
        return self.accounts.get(account_number)  # Returns None if not found
    
    def get_account_by_card(self, card_number: str) -> Account:
        if card_number not in self.cards:
            return None
        
        card = self.cards[card_number]
        return self.get_account(card.account_number)
    
    def set_current_atm(self, atm_id: str) -> bool:
        if atm_id in self.atms:
            self.current_atm = self.atms[atm_id]
            return True
        return False
    
    def process_request(self, request: Request, atm_id: str = None) -> dict:
        """Process request through ATM_System (alternative to ATM.process_request)"""
        # Use specified ATM or current ATM
        atm = self.atms.get(atm_id) if atm_id else self.current_atm
        
        if not atm:
            return {"success": False, "message": "No ATM available"}
        
        return atm.process_request(request, self)

