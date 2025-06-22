from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
import uuid
from abc import ABC, abstractmethod

# Enums for better type safety
class SeatType(Enum):
    ECONOMY = "Economy"
    BUSINESS = "Business"
    FIRST = "First"

class BookingStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    PENDING = "Pending"

class PaymentStatus(Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    PENDING = "Pending"

class UserType(Enum):
    PASSENGER = "Passenger"
    ADMIN = "Admin"
    CREW_MEMBER = "CrewMember"

class CrewMemberType(Enum):
    PILOT = "Pilot"
    CO_PILOT = "CoPilot"
    FLIGHT_ATTENDANT = "FlightAttendant"
    PURSER = "Purser"
    FLIGHT_ENGINEER = "FlightEngineer"

class CrewMemberStatus(Enum):
    ACTIVE = "Active"
    ON_LEAVE = "OnLeave"
    UNAVAILABLE = "Unavailable"
    RETIRED = "Retired"

class Coupon(ABC):
    @abstractmethod
    def apply(self, amount: float) -> float:
        """Apply the coupon to the given amount and return the discounted amount."""
        pass

class PercentageCoupon(Coupon):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def apply(self, amount: float) -> float:
        return amount * (1 - self.percentage / 100)
    
class FixedAmountCoupon(Coupon):
    def __init__(self, discount: float):
        self.discount = discount

    def apply(self, amount: float) -> float:
        return max(0, amount - self.discount)

class User:
    def __init__(self, user_id: str, name: str, email: str, phone: str, user_type: UserType):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.user_type = user_type
        self.created_at = datetime.now()

class Passenger(User):
    def __init__(self, user_id: str, name: str, email: str, phone: str):
        super().__init__(user_id, name, email, phone, UserType.PASSENGER)
        self.bookings: List[str] = []  # booking IDs
        
    def add_booking(self, booking_id: str):
        self.bookings.append(booking_id)
        
    def remove_booking(self, booking_id: str):
        if booking_id in self.bookings:
            self.bookings.remove(booking_id)

class Admin(User):
    def __init__(self, user_id: str, name: str, email: str, phone: str):
        super().__init__(user_id, name, email, phone, UserType.ADMIN)

class CrewMember(User):
    def __init__(self, user_id: str, name: str, email: str, phone: str, 
                 employee_id: str, crew_type: CrewMemberType, hire_date: datetime,
                 base_location: str):
        super().__init__(user_id, name, email, phone, UserType.CREW_MEMBER)
        self.employee_id = employee_id
        self.crew_type = crew_type
        self.hire_date = hire_date
        self.base_location = base_location
        self.status = CrewMemberStatus.ACTIVE
        self.assigned_flights: List[str] = []  # flight IDs
        self.certifications: List[str] = []
        self.flight_hours = 0
        self.last_medical_check: Optional[datetime] = None
        self.next_training_due: Optional[datetime] = None
        
    def assign_flight(self, flight_id: str):
        """Assign crew member to a flight"""
        if self.status == CrewMemberStatus.ACTIVE and flight_id not in self.assigned_flights:
            self.assigned_flights.append(flight_id)
            return True
        return False
    
    def unassign_flight(self, flight_id: str):
        """Remove crew member from a flight"""
        if flight_id in self.assigned_flights:
            self.assigned_flights.remove(flight_id)
            return True
        return False
    
    def add_certification(self, certification: str):
        """Add a certification to crew member"""
        if certification not in self.certifications:
            self.certifications.append(certification)
    
    def update_flight_hours(self, hours: float):
        """Update total flight hours"""
        self.flight_hours += hours
    
    def set_status(self, status: CrewMemberStatus):
        """Update crew member status"""
        self.status = status
        if status != CrewMemberStatus.ACTIVE:
            # Remove from all assigned flights if not active
            self.assigned_flights.clear()
    
    def is_available_for_flight(self, departure_time: datetime, arrival_time: datetime) -> bool:
        """Check if crew member is available for a specific flight time"""
        if self.status != CrewMemberStatus.ACTIVE:
            return False
        
        # Additional logic could be added here to check for:
        # - Maximum duty hours regulations
        # - Required rest periods
        # - Conflicting flight assignments
        
        return True

class Seat:
    def __init__(self, seat_number: str, seat_type: SeatType, price: float):
        self.seat_number = seat_number
        self.seat_type = seat_type
        self.price = price
        self.is_available = True
    
    def reserve(self):
        self.is_available = False

    def release(self):
        self.is_available = True

class FlightCompany:
    def __init__(self, company_id: str, name: str, code: str):
        self.company_id = company_id
        self.name = name
        self.code = code
        self._flights: List[str] = [] # A list of flights

    def add_flights(self, flight_id: str):
        self._flights.append(flight_id)

    def get_flights(self):
        return self._flights

class CrewAssignment:
    def __init__(self, assignment_id: str, flight_id: str, crew_member_id: str, 
                 assigned_at: datetime):
        self.assignment_id = assignment_id
        self.flight_id = flight_id
        self.crew_member_id = crew_member_id
        self.assigned_at = assigned_at
        self.is_confirmed = False
        
    def confirm_assignment(self):
        self.is_confirmed = True

class Flight:
    def __init__(self, flight_id: str, flight_number: str, company_id: str, 
                 source: str, destination: str, departure_time: datetime, 
                 arrival_time: datetime, total_seats: int):
        self.flight_id = flight_id
        self.flight_number = flight_number
        self.company_id = company_id
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.seats: Dict[str, Seat] = {}
        self.available_seats = total_seats
        self.crew_assignments: List[str] = []  # CrewAssignment IDs
        self.required_crew = self._get_required_crew()
        self._initialize_seats(total_seats)
        
    def _get_required_crew(self) -> Dict[CrewMemberType, int]:
        """Define minimum crew requirements for the flight"""
        return {
            CrewMemberType.PILOT: 1,
            CrewMemberType.CO_PILOT: 1,
            CrewMemberType.FLIGHT_ATTENDANT: 4,  # Minimum for a typical commercial flight
            CrewMemberType.PURSER: 1
        }
        
    def _initialize_seats(self, total_seats: int):
        # Simple seat allocation: 70% Economy, 20% Business, 10% First
        economy_count = int(total_seats * 0.7)
        business_count = int(total_seats * 0.2)
        first_count = total_seats - economy_count - business_count
        
        seat_num = 1
        
        # First class seats
        for i in range(first_count):
            seat_id = f"F{seat_num}"
            self.seats[seat_id] = Seat(seat_id, SeatType.FIRST, 500.0)
            seat_num += 1
            
        # Business class seats
        for i in range(business_count):
            seat_id = f"B{seat_num}"
            self.seats[seat_id] = Seat(seat_id, SeatType.BUSINESS, 300.0)
            seat_num += 1
            
        # Economy seats
        for i in range(economy_count):
            seat_id = f"E{seat_num}"
            self.seats[seat_id] = Seat(seat_id, SeatType.ECONOMY, 100.0)
            seat_num += 1
    
    def get_available_seats(self, seat_type: Optional[SeatType] = None) -> List[Seat]:
        available = [seat for seat in self.seats.values() if seat.is_available]
        if seat_type:
            available = [seat for seat in available if seat.seat_type == seat_type]
        return available
    
    def reserve_seat(self, seat_number: str) -> bool:
        if seat_number in self.seats and self.seats[seat_number].is_available:
            self.seats[seat_number].reserve()
            self.available_seats -= 1
            return True
        return False
    
    def release_seat(self, seat_number: str) -> bool:
        if seat_number in self.seats and not self.seats[seat_number].is_available:
            self.seats[seat_number].release()
            self.available_seats += 1
            return True
        return False
    
    def add_crew_assignment(self, assignment_id: str):
        """Add crew assignment to flight"""
        if assignment_id not in self.crew_assignments:
            self.crew_assignments.append(assignment_id)
    
    def remove_crew_assignment(self, assignment_id: str):
        """Remove crew assignment from flight"""
        if assignment_id in self.crew_assignments:
            self.crew_assignments.remove(assignment_id)
    
    def get_flight_duration(self) -> timedelta:
        """Calculate flight duration"""
        return self.arrival_time - self.departure_time

class Payment:
    def __init__(self, payment_id: str, booking_id: str, amount: float, 
                 payment_method: str = "Credit Card"):
        self.payment_id = payment_id
        self.booking_id = booking_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = PaymentStatus.PENDING
        self.created_at = datetime.now()
        self.processed_at: Optional[datetime] = None
    
    def process_payment(self) -> bool:
        # Simulate payment processing
        # In real implementation, this would integrate with payment gateway
        try:
            # Simulate success (90% success rate)
            import random
            if random.random() < 0.9:
                self.status = PaymentStatus.SUCCESS
                self.processed_at = datetime.now()
                return True
            else:
                self.status = PaymentStatus.FAILED
                return False
        except Exception:
            self.status = PaymentStatus.FAILED
            return False

class BookingRequest:
    def __init__(self, passenger_id: str, flight_id: str, seat_type: SeatType, 
                 preferred_seat: Optional[str] = None, coupon: Optional[Coupon] = None):
        self.passenger_id = passenger_id
        self.flight_id = flight_id
        self.seat_type = seat_type
        self.preferred_seat = preferred_seat
        self.created_at = datetime.now()
        self.coupon = coupon

class Booking:
    def __init__(self, booking_id: str, passenger_id: str, flight_id: str, 
                 seat_number: str, amount: float, coupon: Optional[Coupon] = None):
        if coupon:
            amount = coupon.apply(amount)
        if amount < 0:
            raise ValueError("Amount cannot be negative after applying coupon")
        self.booking_id = booking_id
        self.passenger_id = passenger_id
        self.flight_id = flight_id
        self.seat_number = seat_number
        self.amount = amount
        self.status = BookingStatus.PENDING
        self.created_at = datetime.now()
        self.payment_id: Optional[str] = None
    
    def confirm(self, payment_id: str):
        self.status = BookingStatus.CONFIRMED
        self.payment_id = payment_id
    
    def cancel(self):
        self.status = BookingStatus.CANCELLED

class CancelRequest:
    def __init__(self, booking_id: str, passenger_id: str, reason: str = ""):
        self.booking_id = booking_id
        self.passenger_id = passenger_id
        self.reason = reason
        self.created_at = datetime.now()

class SearchRequest:
    def __init__(self, source: str, destination: str, departure_date: datetime,
                 seat_type: Optional[SeatType] = None, max_price: Optional[float] = None):
        self.source = source
        self.destination = destination
        self.departure_date = departure_date
        self.seat_type = seat_type
        self.max_price = max_price
        self.created_at = datetime.now()

class CrewSchedulingRequest:
    def __init__(self, flight_id: str, required_crew: Dict[CrewMemberType, int]):
        self.flight_id = flight_id
        self.required_crew = required_crew
        self.created_at = datetime.now()

class AirlineManagementSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.flights: Dict[str, Flight] = {}
        self.flight_companies: Dict[str, FlightCompany] = {}
        self.bookings: Dict[str, Booking] = {}
        self.payments: Dict[str, Payment] = {}
        self.crew_assignments: Dict[str, CrewAssignment] = {}

    def register_passenger(self, name: str, email: str, phone: str) -> str:
        user_id = str(uuid.uuid4())
        passenger = Passenger(user_id, name, email, phone)
        self.users[user_id] = passenger
        return user_id

    def register_admin(self, name: str, email: str, phone: str) -> str:
        user_id = str(uuid.uuid4())
        admin = Admin(user_id, name, email, phone)
        self.users[user_id] = admin
        return user_id
    
    def register_crew_member(self, name: str, email: str, phone: str, 
                           employee_id: str, crew_type: CrewMemberType, 
                           hire_date: datetime, base_location: str) -> str:
        user_id = str(uuid.uuid4())
        crew_member = CrewMember(user_id, name, email, phone, employee_id, 
                                crew_type, hire_date, base_location)
        self.users[user_id] = crew_member
        return user_id
    
    def add_company(self, name: str, code: str) -> str:
        company_id = str(uuid.uuid4())
        company = FlightCompany(company_id, name, code)
        self.flight_companies[company_id] = company
        return company_id
    
    def add_flight(self, flight_number: str, company_id: str, source: str, 
                   destination: str, departure_time: datetime, arrival_time: datetime,
                   total_seats: int = 150) -> str:
        if company_id not in self.flight_companies:
            raise ValueError("Company not found")
            
        flight_id = str(uuid.uuid4())
        flight = Flight(flight_id, flight_number, company_id, source, 
                       destination, departure_time, arrival_time, total_seats)
        self.flights[flight_id] = flight
        self.flight_companies[company_id].add_flights(flight_id)
        return flight_id
    
    def assign_crew_to_flight(self, flight_id: str, crew_member_id: str) -> Optional[str]:
        """Assign a crew member to a flight"""
        if (flight_id not in self.flights or crew_member_id not in self.users):
            return None
        
        flight = self.flights[flight_id]
        crew_member = self.users[crew_member_id]
        
        if not isinstance(crew_member, CrewMember):
            return None
        
        # Check if crew member is available for this flight
        if not crew_member.is_available_for_flight(flight.departure_time, flight.arrival_time):
            return None
        
        # Create crew assignment
        assignment_id = str(uuid.uuid4())
        assignment = CrewAssignment(assignment_id, flight_id, crew_member_id, datetime.now())
        
        # Add assignment to both flight and crew member
        if crew_member.assign_flight(flight_id):
            flight.add_crew_assignment(assignment_id)
            self.crew_assignments[assignment_id] = assignment
            return assignment_id
        
        return None
    
    def unassign_crew_from_flight(self, assignment_id: str) -> bool:
        """Remove crew assignment"""
        if assignment_id not in self.crew_assignments:
            return False
        
        assignment = self.crew_assignments[assignment_id]
        flight = self.flights.get(assignment.flight_id)
        crew_member = self.users.get(assignment.crew_member_id)
        
        if flight and isinstance(crew_member, CrewMember):
            flight.remove_crew_assignment(assignment_id)
            crew_member.unassign_flight(assignment.flight_id)
            del self.crew_assignments[assignment_id]
            return True
        
        return False
    
    def get_available_crew(self, departure_time: datetime, arrival_time: datetime, 
                          crew_type: Optional[CrewMemberType] = None) -> List[CrewMember]:
        """Get available crew members for a specific time period"""
        available_crew = []
        
        for user in self.users.values():
            if (isinstance(user, CrewMember) and 
                user.is_available_for_flight(departure_time, arrival_time)):
                
                if crew_type is None or user.crew_type == crew_type:
                    available_crew.append(user)
        
        return available_crew
    
    def get_flight_crew(self, flight_id: str) -> List[CrewMember]:
        """Get all crew members assigned to a flight"""
        if flight_id not in self.flights:
            return []
        
        flight = self.flights[flight_id]
        crew_members = []
        
        for assignment_id in flight.crew_assignments:
            if assignment_id in self.crew_assignments:
                assignment = self.crew_assignments[assignment_id]
                crew_member = self.users.get(assignment.crew_member_id)
                if isinstance(crew_member, CrewMember):
                    crew_members.append(crew_member)
        
        return crew_members
    
    def search_flight(self, search_request: SearchRequest) -> List[Flight]:
        matching_flights = []
        
        for flight in self.flights.values():
            # Basic matching criteria
            if (flight.source.lower() == search_request.source.lower() and
                flight.destination.lower() == search_request.destination.lower() and
                flight.departure_time.date() == search_request.departure_date.date()):
                
                # Check seat type availability if specified
                if search_request.seat_type:
                    available_seats = flight.get_available_seats(search_request.seat_type)
                    if not available_seats:
                        continue
                    
                    # Check price constraint if specified
                    if search_request.max_price:
                        min_price = min(seat.price for seat in available_seats)
                        if min_price > search_request.max_price:
                            continue
                
                matching_flights.append(flight)
        
        # Sort by departure time
        matching_flights.sort(key=lambda f: f.departure_time)
        return matching_flights
    
    def create_booking(self, booking_request: BookingRequest) -> Optional[str]:
        if (booking_request.passenger_id not in self.users or 
            booking_request.flight_id not in self.flights):
            return None
        
        flight = self.flights[booking_request.flight_id]
        available_seats = flight.get_available_seats(booking_request.seat_type)

        if not available_seats:
            return None

        selected_seat = None
        if booking_request.preferred_seat and booking_request.preferred_seat in flight.seats:
            preferred = flight.seats[booking_request.preferred_seat]
            if preferred.is_available and preferred.seat_type == booking_request.seat_type:
                selected_seat = preferred

        if not selected_seat:
            selected_seat = available_seats[0]

        if not flight.reserve_seat(selected_seat.seat_number):
            return None
        
        booking_id = str(uuid.uuid4())
        booking = Booking(booking_id, booking_request.passenger_id, 
                         booking_request.flight_id, selected_seat.seat_number, 
                         selected_seat.price, booking_request.coupon)
        self.bookings[booking_id] = booking

        passenger = self.users[booking_request.passenger_id]
        if isinstance(passenger, Passenger):
            passenger.add_booking(booking_id)
        
        return booking_id
    
    def process_payment_and_confirm(self, booking_id: str, payment_method: str = "Credit Card") -> bool:
        if booking_id not in self.bookings:
            return False
        
        booking = self.bookings[booking_id]
        if booking.status != BookingStatus.PENDING:
            return False
        
        # Create and process payment
        payment_id = str(uuid.uuid4())
        payment = Payment(payment_id, booking_id, booking.amount, payment_method)
        
        if payment.process_payment():
            self.payments[payment_id] = payment
            booking.confirm(payment_id)
            return True
        else:
            # Release the seat if payment failed
            flight = self.flights[booking.flight_id]
            flight.release_seat(booking.seat_number)
            booking.cancel()
            return False
        
    def cancel_booking(self, cancel_request: CancelRequest) -> bool:
        booking_id = cancel_request.booking_id
        
        if (booking_id not in self.bookings or 
            self.bookings[booking_id].passenger_id != cancel_request.passenger_id):
            return False
        
        booking = self.bookings[booking_id]
        if booking.status != BookingStatus.CONFIRMED:
            return False
        
        # Release the seat
        flight = self.flights[booking.flight_id]
        flight.release_seat(booking.seat_number)
        
        # Cancel booking
        booking.cancel()
        
        # Remove from passenger's bookings
        passenger = self.users[booking.passenger_id]
        if isinstance(passenger, Passenger):
            passenger.remove_booking(booking_id)
        
        return True
    
    def get_user_bookings(self, user_id: str) -> List[Booking]:
        user = self.users.get(user_id)
        if not isinstance(user, Passenger):
            return []
        
        return [self.bookings[booking_id] for booking_id in user.bookings 
                if booking_id in self.bookings]
    
    def get_crew_schedule(self, crew_member_id: str) -> List[Flight]:
        """Get all flights assigned to a crew member"""
        crew_member = self.users.get(crew_member_id)
        if not isinstance(crew_member, CrewMember):
            return []
        
        return [self.flights[flight_id] for flight_id in crew_member.assigned_flights 
                if flight_id in self.flights]
    
    def get_flight_details(self, flight_id: str) -> Optional[Flight]:
        return self.flights.get(flight_id)