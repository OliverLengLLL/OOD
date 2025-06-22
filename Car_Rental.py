from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import uuid

class CarType(Enum):
    ECONOMY = "economy"
    COMPACT = "compact"
    INTERMEDIATE = "intermediate"
    STANDARD = "standard"
    FULL_SIZE = "full_size"
    PREMIUM = "premium"
    LUXURY = "luxury"

class CarStatus(Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance" 
    OUT_OF_SERVICE = "out_of_service"

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"
    DIGITAL_WALLET = "digital_wallet"

class DrivingLicense:
    def __init__(self, license_number: str, expiry_date: datetime, issued_country: str, issued_state: str):
        self.license_number = license_number
        self.expiry_date = expiry_date
        self.issued_country = issued_country
        self.issued_state = issued_state
    
    def is_valid(self) -> bool:
        return self.expiry_date > datetime.now()
    
class Customer:
    def __init__(self, customer_id: str, name: str, email: str, 
                 phone: str, address: str, driving_license: DrivingLicense):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.driving_license = driving_license
        self.booking_history: List[str] = []  # booking IDs
    
    def can_rent_car(self) -> bool:
        return self.driving_license.is_valid()
    
class Location:
    def __init__(self, location_id: str, name: str, address: str, 
                 city: str, state: str, zip_code: str):
        self.location_id = location_id
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code

class Car:
    def __init__(self, car_id: str, license_plate: str, make: str, 
                 model: str, year: int, car_type: CarType, 
                 daily_rate: float, location: Location):
        self.car_id = car_id
        self.license_plate = license_plate
        self.make = make
        self.model = model
        self.year = year
        self.car_type = car_type
        self.daily_rate = daily_rate
        self.status = CarStatus.AVAILABLE
        self.location = location
        self.mileage = 0
        self.features: List[str] = []

    def is_available(self) -> bool:
        return self.status == CarStatus.AVAILABLE
    
    def rent(self) -> bool:
        if self.is_available():
            self.status = CarStatus.RENTED
            return True
        return False
    
    def return_car(self) -> bool:
        if self.status == CarStatus.RENTED:
            self.status = CarStatus.AVAILABLE
            return True
        return False
    
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        # Simulate credit card processing
        card_number = payment_details.get('card_number')
        cvv = payment_details.get('cvv')
        expiry = payment_details.get('expiry')
        
        # Basic validation simulation
        if card_number and cvv and expiry:
            print(f"Processing credit card payment of ${amount}")
            return True
        return False

class DebitCardPayment(PaymentStrategy):
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        # Simulate debit card processing
        print(f"Processing debit card payment of ${amount}")
        return True

class CashPayment(PaymentStrategy):
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        print(f"Processing cash payment of ${amount}")
        return True

class Payment:
    def __init__(self, payment_id: str, amount: float, 
                 payment_method: PaymentMethod, payment_details: Dict):
        self.payment_id = payment_id
        self.amount = amount
        self.payment_method = payment_method
        self.payment_details = payment_details
        self.status = PaymentStatus.PENDING
        self.payment_date: Optional[datetime] = None
        self.payment_strategy = self._get_payment_strategy()
    
    def _get_payment_strategy(self) -> PaymentStrategy:
        strategies = {
            PaymentMethod.CREDIT_CARD: CreditCardPayment(),
            PaymentMethod.DEBIT_CARD: DebitCardPayment(),
            PaymentMethod.CASH: CashPayment(),
            PaymentMethod.DIGITAL_WALLET: CreditCardPayment()  # Similar to credit card
        }
        return strategies.get(self.payment_method, CashPayment())
    
    def process(self) -> bool:
        success = self.payment_strategy.process_payment(self.amount, self.payment_details)
        if success:
            self.status = PaymentStatus.COMPLETED
            self.payment_date = datetime.now()
        else:
            self.status = PaymentStatus.FAILED
        return success

class Booking:
    def __init__(self, booking_id: str, customer: Customer, car: Car,
                 pickup_date: datetime, return_date: datetime,
                 pickup_location: Location, return_location: Location):
        self.booking_id = booking_id
        self.customer = customer
        self.car = car
        self.pickup_date = pickup_date
        self.return_date = return_date
        self.pickup_location = pickup_location
        self.return_location = return_location
        self.status = BookingStatus.PENDING
        self.total_amount = self._calculate_total_amount()
        self.payment: Optional[Payment] = None
        self.created_date = datetime.now()
        self.actual_return_date: Optional[datetime] = None
    
    def _calculate_total_amount(self) -> float:
        days = (self.return_date - self.pickup_date).days
        if days <= 0:
            days = 1  # Minimum 1 day rental
        
        base_amount = days * self.car.daily_rate
        
        # Add fees (taxes, insurance, etc.)
        tax_rate = 0.1  # 10% tax
        insurance_per_day = 15.0
        
        total = base_amount + (days * insurance_per_day)
        total += total * tax_rate
        
        return round(total, 2)
    
    def confirm_booking(self) -> bool:
        if (self.status == BookingStatus.PENDING and 
            self.car.is_available() and 
            self.customer.can_rent_car()):
            
            if self.car.rent():
                self.status = BookingStatus.CONFIRMED
                self.customer.booking_history.append(self.booking_id)
                return True
        return False
    
    def cancel_booking(self) -> bool:
        if self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            self.status = BookingStatus.CANCELLED
            self.car.return_car()
            return True
        return False
    
    def complete_booking(self) -> bool:
        if self.status == BookingStatus.CONFIRMED:
            self.status = BookingStatus.COMPLETED
            self.actual_return_date = datetime.now()
            self.car.return_car()
            return True
        return False

class SearchRequest:
    def __init__(self, car_type: Optional[CarType] = None,
                 pickup_location: Optional[Location] = None,
                 pickup_date: Optional[datetime] = None,
                 return_date: Optional[datetime] = None,
                 max_price: Optional[float] = None):
        self.car_type = car_type
        self.pickup_location = pickup_location
        self.pickup_date = pickup_date
        self.return_date = return_date
        self.max_price = max_price

class BookingRequest:
    def __init__(self, customer: Customer, car: Car,
                 pickup_date: datetime, return_date: datetime,
                 pickup_location: Location, return_location: Location,
                 payment_method: PaymentMethod, payment_details: Dict):
        self.customer = customer
        self.car = car
        self.pickup_date = pickup_date
        self.return_date = return_date
        self.pickup_location = pickup_location
        self.return_location = return_location
        self.payment_method = payment_method
        self.payment_details = payment_details

class CancelRequest:
    def __init__(self, booking_id: str, customer_id: str, reason: str = ""):
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.reason = reason
        self.requested_date = datetime.now()

class CarRentalSystem:
    def __init__(self):
        self.cars: Dict[str, Car] = {}
        self.customers: Dict[str, Customer] = {}
        self.bookings: Dict[str, Booking] = {}
        self.locations: Dict[str, Location] = {}
        self.payments: Dict[str, Payment] = {}
    
    def add_car(self, car: Car) -> bool:
        """Add a new car to the system"""
        if car.car_id not in self.cars:
            self.cars[car.car_id] = car
            return True
        return False
    
    def add_customer(self, customer: Customer) -> bool:
        """Add a new customer to the system"""
        if customer.customer_id not in self.customers:
            self.customers[customer.customer_id] = customer
            return True
        return False
    
    def add_location(self, location: Location) -> bool:
        """Add a new location to the system"""
        if location.location_id not in self.locations:
            self.locations[location.location_id] = location
            return True
        return False
    
    def search_cars(self, search_request: SearchRequest) -> List[Car]:
        """Search for available cars based on criteria"""
        available_cars = []
        
        for car in self.cars.values():
            if not car.is_available():
                continue
            
            # Filter by car type
            if (search_request.car_type and 
                car.car_type != search_request.car_type):
                continue
            
            # Filter by location
            if (search_request.pickup_location and 
                car.location.location_id != search_request.pickup_location.location_id):
                continue
            
            # Filter by price
            if (search_request.max_price and 
                car.daily_rate > search_request.max_price):
                continue
            
            available_cars.append(car)
        
        # Sort by daily rate (cheapest first)
        available_cars.sort(key=lambda x: x.daily_rate)
        return available_cars
    
    def create_booking(self, booking_request: BookingRequest) -> Optional[Booking]:
        """Create a new booking"""
        # Validate request
        if not booking_request.customer.can_rent_car():
            return None
        
        if not booking_request.car.is_available():
            return None
        
        if booking_request.pickup_date >= booking_request.return_date:
            return None
        
        # Create booking
        booking_id = str(uuid.uuid4())
        booking = Booking(
            booking_id=booking_id,
            customer=booking_request.customer,
            car=booking_request.car,
            pickup_date=booking_request.pickup_date,
            return_date=booking_request.return_date,
            pickup_location=booking_request.pickup_location,
            return_location=booking_request.return_location
        )
        
        # Process payment
        payment_id = str(uuid.uuid4())
        payment = Payment(
            payment_id=payment_id,
            amount=booking.total_amount,
            payment_method=booking_request.payment_method,
            payment_details=booking_request.payment_details
        )
        
        if payment.process():
            booking.payment = payment
            self.payments[payment_id] = payment
            
            if booking.confirm_booking():
                self.bookings[booking_id] = booking
                return booking
        
        return None
    
    def cancel_booking(self, cancel_request: CancelRequest) -> bool:
        """Cancel an existing booking"""
        booking = self.bookings.get(cancel_request.booking_id)
        
        if not booking:
            return False
        
        # Verify customer ownership
        if booking.customer.customer_id != cancel_request.customer_id:
            return False
        
        # Check if cancellation is allowed
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return False
        
        # Process cancellation
        if booking.cancel_booking():
            # Process refund if payment was made
            if booking.payment and booking.payment.status == PaymentStatus.COMPLETED:
                booking.payment.status = PaymentStatus.REFUNDED
            return True
        
        return False
    
    def return_car(self, booking_id: str, return_mileage: int = 0) -> bool:
        """Process car return"""
        booking = self.bookings.get(booking_id)
        
        if not booking:
            return False
        
        if booking.status != BookingStatus.CONFIRMED:
            return False
        
        # Update car mileage
        booking.car.mileage += return_mileage
        
        # Complete booking
        return booking.complete_booking()
    
    def get_customer_bookings(self, customer_id: str) -> List[Booking]:
        """Get all bookings for a customer"""
        customer_bookings = []
        for booking in self.bookings.values():
            if booking.customer.customer_id == customer_id:
                customer_bookings.append(booking)
        
        # Sort by creation date (newest first)
        customer_bookings.sort(key=lambda x: x.created_date, reverse=True)
        return customer_bookings
    
    def get_available_cars_count(self) -> int:
        """Get count of available cars"""
        return len([car for car in self.cars.values() if car.is_available()])
    
    def get_revenue_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate revenue report for a date range"""
        total_revenue = 0.0
        total_bookings = 0
        completed_bookings = 0
        
        for booking in self.bookings.values():
            if (start_date <= booking.created_date <= end_date):
                total_bookings += 1
                if (booking.status == BookingStatus.COMPLETED and 
                    booking.payment and 
                    booking.payment.status == PaymentStatus.COMPLETED):
                    total_revenue += booking.total_amount
                    completed_bookings += 1
        
        return {
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'average_booking_value': total_revenue / completed_bookings if completed_bookings > 0 else 0
        }


