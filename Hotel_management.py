from enum import Enum
from datetime import datetime, date
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import uuid

class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    DELUXE = "DELUXE"
    SUITE = "SUITE"

class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"

class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    REFUNDED = "REFUNDED"

class Address:
    def __init__(self, street: str, city: str, state: str, zip_code: str, country: str):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

class Guest:
    def __init__(self, guest_id: str, name: str, email: str, phone: str, address: Address):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.bookings: List['Booking'] = []

class Room:
    def __init__(self, room_number: str, room_type: RoomType, price_per_night: float):
        self.room_number = room_number
        self.room_type = room_type
        self.room_status = RoomStatus.AVAILABLE
        self.price_per_night = price_per_night
        self.features: List[str] = []

    def is_available(self, check_in: date, check_out:date):
        #TODO we need to check against the DB for the check in and out date
        return self.room_status == RoomStatus.AVAILABLE
    
    def add_features(self, feature: str):
        self.features.append(feature)

class Booking:
    def __init__(self, booking_id: str, guest: Guest, rooms: List[Room], check_in_date: date, check_out_date: date):
            self.booking_id = booking_id
            self.guest = guest
            self.rooms = rooms
            self.check_in_date = check_in_date
            self.check_out_date = check_out_date
            self.booking_date = datetime.now()
            self.status = BookingStatus.CONFIRMED
            self.total_amount = self._calculate_total_amount()
            self.payment: Optional['Payment'] = None
    
    def _calculate_total_amount(self) -> float:
        nights = (self.check_out_date - self.check_in_date).days
        total = sum(room.price_per_night * nights for room in self.rooms)
        return total
    
    def cancel_booking(self):
        self.status = BookingStatus.CANCELLED
        # Release rooms
        for room in self.rooms:
            if room.status == RoomStatus.RESERVED:
                room.status = RoomStatus.AVAILABLE

class Payment:
    def __init__(self, payment_id: str, booking: Booking, amount: float):
        self.payment_id = payment_id
        self.booking = booking
        self.amount = amount
        self.payment_date = datetime.now()
        self.status = PaymentStatus.PENDING
    
    def process_payment(self) -> bool:
        # Simulate payment processing
        self.status = PaymentStatus.PAID
        return True
    
    def refund_payment(self) -> bool:
        if self.status == PaymentStatus.PAID:
            self.status = PaymentStatus.REFUNDED
            return True
        return False
    
class RoomService:
    def __init__(self):
        #Room according to the room number
        self.rooms: Dict[str, Room] = {}
    
    def add_room(self, room: Room):
        self.rooms[room.room_number] = room
    
    def get_available_rooms(self, room_type: RoomType, check_in: date, check_out: date) -> List[Room]:
        available_rooms = []
        for room in self.rooms.values():
            if (room.room_type == room_type and room.is_available(check_in, check_out)):
                available_rooms.append(room)
        return available_rooms
    
    def get_room(self, room_number: str) -> Optional[Room]:
        return self.rooms.get(room_number)
    
    def update_room_status(self, room_number: str, status: RoomStatus):
        if room_number in self.rooms:
            self.rooms[room_number].status = status

class BookingService:
    def __init__(self, room_service: RoomService):
        self.bookings: Dict[str, Booking] = {}
        self.room_servoce = room_service

    def create_booking(self, guest: Guest, room_numbers: List[str], check_in_date: date, check_out_date: date) -> Optional[Booking]:
        if check_in_date >= check_out_date or check_in_date < date.today():
            return None
        
        rooms = []
        for room_number in room_numbers:
            room = self.room_service.get_room(room_number)
            if not room or not room.is_available(check_in_date, check_out_date):
                return None
            rooms.append(room)
        
        booking_id = str(uuid.uuid4())
        booking = Booking(booking_id, guest, rooms, check_in_date, check_out_date)

        for room in rooms:
            room.status = RoomStatus.RESERVED
        
        self.bookings[booking_id] = booking
        guest.bookings.append(booking)
        
        return booking
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        return self.bookings.get(booking_id)
    
    def cancel_booking(self, booking_id: str) -> bool:
        booking = self.bookings.get(booking_id)
        if booking and booking.status == BookingStatus.CONFIRMED:
            booking.cancel_booking()
            return True
        return False
    
    def check_in(self, booking_id: str) -> bool:
        booking = self.bookings.get(booking_id)
        if booking and booking.status == BookingStatus.CONFIRMED:
            booking.status = BookingStatus.CHECKED_IN
            for room in booking.rooms:
                room.status = RoomStatus.OCCUPIED
            return True
        return False

    def check_out(self, booking_id: str) -> bool:
        booking = self.bookings.get(booking_id)
        if booking and booking.status == BookingStatus.CHECKED_IN:
            booking.status = BookingStatus.CHECKED_OUT
            for room in booking.rooms:
                room.status = RoomStatus.AVAILABLE
            return True
        return False
    
class GuestService:
    def __init__(self):
        self.guests: Dict[str, Guest] = {}
    
    def register_guest(self, name: str, email: str, phone: str, address: Address) -> Guest:
        guest_id = str(uuid.uuid4())
        guest = Guest(guest_id, name, email, phone, address)
        self.guests[guest_id] = guest
        return guest
    
    def get_guest(self, guest_id: str) -> Optional[Guest]:
        return self.guests.get(guest_id)
    
    def find_guest_by_email(self, email: str) -> Optional[Guest]:
        for guest in self.guests.values():
            if guest.email == email:
                return guest
        return None

class HotelManagementSystem:
    def __init__(self, hotel_name: str):
        self.hotel_name = hotel_name
        self.room_service = RoomService()
        self.booking_service = BookingService(self.room_service)
        self.payment_service = PaymentService()
        self.guest_service = GuestService()


    def add_room(self, room_number: str, room_type: RoomType, price_per_night: float):
        room = Room(room_number, room_type, price_per_night)
        self.room_service.add_room(room)

    def search_rooms(self, room_type: RoomType, check_in: date, check_out: date) -> List[Room]:
        return self.room_service.get_available_rooms(room_type, check_in, check_out)
    
    def make_reservation(self, guest_email: str, room_numbers: List[str], check_in_date: date, check_out_date: date) -> Optional[str]:
        guest = self.guest_service.find_guest_by_email(guest_email)
        if not guest:
            return None
        
        booking = self.booking_service.create_booking(
            guest, room_numbers, check_in_date, check_out_date
        )
        
        if booking:
            payment = self.payment_service.create_payment(booking)
            return booking.booking_id
        return None
    
    def check_in_guest(self, booking_id: str) -> bool:
        return self.booking_service.check_in(booking_id)
    
    def check_out_guest(self, booking_id: str) -> bool:
        return self.booking_service.check_out(booking_id)
    
    def cancel_reservation(self, booking_id: str) -> bool:
        return self.booking_service.cancel_booking(booking_id)



class RoomComponent(ABC):
    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_cost(self):
        pass

class BaseRoom(RoomComponent):
    def __init__(self, room: Room):
        self.room = room

    def get_description(self):
        return f"Room {self.room.room_number} ({self.room.room_type.value})"
    
    def get_cost(self):
        return self.room.price_per_night
    
class DeluxeRoom(BaseRoom):
    def get_description(self):
        return super().get_description() + " - Deluxe Room"
    
    def get_cost(self):
        return super().get_cost() + 100.0  # Additional cost for deluxe room 

class RoomServiceDecorator(RoomComponent):
    def __init__(self, room_component: RoomComponent):
        self.room_component = room_component
    
    def get_description(self) -> str:
        return self.room_component.get_description()
    
    def get_cost(self) -> float:
        return self.room_component.get_cost()
    
class BreakfastService(RoomServiceDecorator):
    def get_description(self) -> str:
        return self.room_component.get_description() + " + Breakfast"
    
    def get_cost(self) -> float:
        return self.room_component.get_cost() + 25.0

class ParkingService(RoomServiceDecorator):
    def get_description(self) -> str:
        return self.room_component.get_description() + " + Parking"
    
    def get_cost(self) -> float:
        return self.room_component.get_cost() + 15.0

class SpaService(RoomServiceDecorator):
    def get_description(self) -> str:
        return self.room_component.get_description() + " + Spa Access"
    
    def get_cost(self) -> float:
        return self.room_component.get_cost() + 50.0

class LaundryService(RoomServiceDecorator):
    def get_description(self) -> str:
        return self.room_component.get_description() + " + Laundry"
    
    def get_cost(self) -> float:
        return self.room_component.get_cost() + 20.0