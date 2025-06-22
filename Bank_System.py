import datetime
from enum import Enum
from typing import List, Optional
import uuid

class AccountType(Enum):
    CHECKING  = "CHECKING"
    SAVING = "SAVING"

class RequestStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Customer:
    def __init__(self, customer_id: str, name: str, email: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.accounts: List['Account'] = []
    
    def add_account(self, account: 'Account'):
        self.accounts.append(account)
    
    def get_accounts(self) -> List['Account']:
        return self.accounts

class Account:
    def __init__(self, account_id: str, customer_id: str, account_type: AccountType, initial_balance: float = 0.0):
        self.account_id = account_id
        self.customer_id = customer_id
        self.account_type = account_type
        self.balance = initial_balance
        self.created_at = datetime.now()
        self.is_active = True
    
    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self.balance += amount
        return True
    
    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True
    
    def get_balance(self) -> float:
        return self.balance
    
    def close_account(self):
        self.is_active = False

class Request:
    def __init__(self, request_id: str, customer_id: str):
        self.request_id = request_id
        self.customer_id = customer_id
        self.status = RequestStatus.PENDING
        self.created_at = datetime.now()
        self.processed_at: Optional[datetime] = None
    
    def approve(self):
        self.status = RequestStatus.APPROVED
        self.processed_at = datetime.now()
    
    def reject(self):
        self.status = RequestStatus.REJECTED
        self.processed_at = datetime.now()

class OpenAccountRequest(Request):
    def __init__(self, request_id: str, customer_id: str, account_type: AccountType, initial_deposit: float = 0.0):
        super().__init__(request_id, customer_id)
        self.account_type = account_type
        self.initial_deposit = initial_deposit

class DepositRequest(Request):
    def __init__(self, request_id: str, customer_id: str, account_id: str, amount: float):
        super().__init__(request_id, customer_id)
        self.account_id = account_id
        self.amount = amount

class WithdrawRequest(Request):
    def __init__(self, request_id: str, customer_id: str, account_id: str, amount: float):
        super().__init__(request_id, customer_id)
        self.account_id = account_id
        self.amount = amount

class Bank:
    def __init__(self, bank_id: int, name: str):
        self.bank_id = bank_id
        self.name = name
        self.customers: dict[str, Customer] = {}
        self.requests: dict[str, Request] = {}
        self.accounts: dict[str, Account] = {}

    def add_customer(self, customer: Customer) -> bool:
        if customer.customer_id in self.customers:
            return False
        self.customers[customer.customer_id] = customer
        return True
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)
    
    def get_account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)
    
    def handle_open_account_request(self, request: OpenAccountRequest) -> bool:
        customer = self.customers[request.customer_id]
        if not customer:
            request.reject()
            return False

        account_id = str(uuid.uuid4())
        new_account = Account(request.customer_id, request.account_type, request.initial_deposit)

        self.accounts[account_id] = new_account
        customer.add_account(new_account)

        request.approve()
        return True
    
    def handle_deposit_request(self, request: DepositRequest) -> bool:
        account = self.accounts[request.account_id]
        if not account or not account.is_active:
            request.reject()
            return False
        
        if account.deposit(request.amount):
            request.approve()
            return True
        else:
            request.reject()
            return False
        
    def handle_withdraw_request(self, request: WithdrawRequest) -> bool:
        account = self.accounts[request.account_id]
        if not account or not account.is_active:
            request.reject()
            return False
        
        if account.withdraw(request.amount):
            request.approve()
            return True
        else:
            request.reject()
            return False

class BankSystem:
    def __init__(self):
        self.banks: dict[str, Bank] = {}

    def add_bank(self, bank: Bank) -> bool:
        if bank.bank_id in self.banks:
            return False

        self.banks[bank.bank_id] = bank
        return True

    def get_bank(self, bank_id: str) -> Optional[Bank]:
        return self.banks.get(bank_id)
    
    def create_customer(self, bank_id: str, name: str, email: str, phone:str):
        bank = self.get_bank(bank_id)
        if not bank:
            return None
        
        customer_id = str(uuid.uuid4())
        customer = Customer(customer_id, name, email, phone)
        
        if bank.add_customer(customer):
            return customer_id
        return None
    
    def open_account(self, bank_id: str, customer_id: str, account_type: AccountType, initial_deposit: float = 0.0) -> bool:
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        request_id = str(uuid.uuid4())
        request = OpenAccountRequest(request_id, customer_id, account_type, initial_deposit)
        bank.requests[request_id] = request

        return bank.handle_open_account_request(request)
    
    def deposit(self, bank_id: str, customer_id: str, amount: float = 0.0) -> bool:
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        request_id = str(uuid.uuid4())
        request = DepositRequest(request_id, customer_id, amount)
        bank.requests[request_id] = request

        return bank.handle_deposit_request(request)
    
    def withdraw(self, bank_id: str, customer_id: str, amount: float = 0.0) -> bool:
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        request_id = str(uuid.uuid4())
        request = WithdrawRequest(request_id, customer_id, amount)
        bank.requests[request_id] = request

        return bank.handle_withdraw_request(request)
    
    def get_account_balance(self, bank_id: str, account_id: str) -> Optional[float]:
        bank = self.get_bank(bank_id)
        if not bank:
            return None
        
        account = bank.get_account(account_id)
        return account.get_balance() if account else None