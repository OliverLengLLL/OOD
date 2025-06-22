from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
import uuid

# Enums
class SeatType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    VIP = "VIP"

class SeatStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    BLOCKED = "BLOCKED"

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class RequestType(Enum):
    BOOK_SEATS = "BOOK_SEATS"
    CANCEL_BOOKING = "CANCEL_BOOKING"
    CHECK_AVAILABILITY = "CHECK_AVAILABILITY"

# Simple Request Classes (Data Holders Only)
class BookingRequest:
    def __init__(self, customer_id: str, show_id: str, seat_ids: List[str], request_type: RequestType = RequestType.BOOK_SEATS):
        self.request_id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.show_id = show_id
        self.seat_ids = seat_ids
        self.request_type = request_type
        self.request_time = datetime.now()
        self.payment_method = None
        
        # Results (populated after processing)
        self.booking_id = None
        self.total_amount = 0.0
        self.status = BookingStatus.PENDING
        self.error_message = None

    def set_payment_method(self, payment_method: str):
        self.payment_method = payment_method

    def get_customer_id(self):
        return self.customer_id
    
    def get_show_id(self):
        return self.show_id
    
    def get_seat_ids(self):
        return self.seat_ids
    
    def get_request_type(self):
        return self.request_type

class CancellationRequest:
    def __init__(self, booking_id: str, customer_id: str):
        self.request_id = str(uuid.uuid4())
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.request_time = datetime.now()
        
        # Results
        self.success = False
        self.refund_amount = 0.0
        self.error_message = None

    def get_booking_id(self):
        return self.booking_id
    
    def get_customer_id(self):
        return self.customer_id

class AvailabilityRequest:
    def __init__(self, show_id: str, seat_count: int = None, seat_type: SeatType = None):
        self.request_id = str(uuid.uuid4())
        self.show_id = show_id
        self.seat_count = seat_count
        self.seat_type = seat_type
        self.request_time = datetime.now()
        
        # Results
        self.available_seats = []
        self.total_available = 0

    def get_show_id(self):
        return self.show_id
    
    def get_seat_count(self):
        return self.seat_count
    
    def get_seat_type(self):
        return self.seat_type

# Supporting Classes
class Movie:
    def __init__(self, movie_id: str, title: str, duration: int, genre: str):
        self.movie_id = movie_id
        self.title = title
        self.duration = duration
        self.genre = genre

class Show:
    def __init__(self, show_id: str, movie: Movie, screen: 'Screen', start_time: datetime):
        self.show_id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        self.end_time = start_time + timedelta(minutes=movie.duration)

class Payment:
    def __init__(self, payment_id: str, amount: float, payment_method: str):
        self.payment_id = payment_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = "PENDING"
        self.transaction_time = None

    def process(self) -> bool:
        # Simple payment simulation
        import random
        success = random.choice([True, True, True, False])  # 75% success
        self.status = "SUCCESS" if success else "FAILED"
        if success:
            self.transaction_time = datetime.now()
        return success

class Booking:
    def __init__(self, booking_id: str, customer_id: str, show: Show, seat_ids: List[str], total_amount: float):
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.show = show
        self.seat_ids = seat_ids
        self.total_amount = total_amount
        self.booking_time = datetime.now()
        self.status = BookingStatus.CONFIRMED
        self.payment = None

    def set_payment(self, payment: Payment):
        self.payment = payment

    def get_booking_details(self) -> Dict:
        return {
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'movie_title': self.show.movie.title,
            'screen_name': self.show.screen.name,
            'show_time': self.show.start_time.strftime('%Y-%m-%d %H:%M'),
            'seats': ', '.join(self.seat_ids),
            'total_amount': self.total_amount,
            'status': self.status.value
        }

# Core Domain Classes
class Seat:
    def __init__(self, seat_id: str, row: str, number: int, seat_type: SeatType, price: float):
        self.seat_id = seat_id
        self.row = row
        self.number = number
        self.seat_type = seat_type
        self.price = price
        self.status = SeatStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == SeatStatus.AVAILABLE

    def block(self) -> bool:
        if self.is_available():
            self.status = SeatStatus.BLOCKED
            return True
        return False

    def book(self) -> bool:
        if self.status == SeatStatus.BLOCKED:
            self.status = SeatStatus.BOOKED
            return True
        return False

    def release(self):
        self.status = SeatStatus.AVAILABLE

    def get_seat_id(self):
        return self.seat_id
    
    def get_price(self):
        return self.price
    
    def get_seat_type(self):
        return self.seat_type

class Screen:
    def __init__(self, screen_id: str, name: str, total_capacity: int):
        self.screen_id = screen_id
        self.name = name
        self.total_capacity = total_capacity
        self.seats: Dict[str, Seat] = {}
        self.shows: Dict[str, Show] = {}
        self._initialize_seats()

    def _initialize_seats(self):
        """Initialize seats with different pricing"""
        rows = ['A', 'B', 'C', 'D', 'E', 'F']
        seats_per_row = self.total_capacity // len(rows)
        
        for i, row in enumerate(rows):
            for seat_num in range(1, seats_per_row + 1):
                seat_id = f"{row}{seat_num}"
                
                # Pricing tiers
                if i < 2:
                    seat_type, price = SeatType.VIP, 300.0
                elif i < 4:
                    seat_type, price = SeatType.PREMIUM, 200.0
                else:
                    seat_type, price = SeatType.REGULAR, 150.0
                
                seat = Seat(seat_id, row, seat_num, seat_type, price)
                self.seats[seat_id] = seat

    def add_show(self, show: Show):
        self.shows[show.show_id] = show

    def get_available_seats(self, seat_type: SeatType = None) -> List[Seat]:
        available = [seat for seat in self.seats.values() if seat.is_available()]
        if seat_type:
            available = [seat for seat in available if seat.seat_type == seat_type]
        return available

    def get_seat(self, seat_id: str) -> Optional[Seat]:
        return self.seats.get(seat_id)

    def check_seats_availability(self, seat_ids: List[str]) -> bool:
        """Check if all requested seats are available"""
        for seat_id in seat_ids:
            seat = self.get_seat(seat_id)
            if not seat or not seat.is_available():
                return False
        return True

    def block_seats(self, seat_ids: List[str]) -> bool:
        """Block seats for reservation"""
        if not self.check_seats_availability(seat_ids):
            return False
        
        for seat_id in seat_ids:
            seat = self.get_seat(seat_id)
            seat.block()
        return True

    def book_seats(self, seat_ids: List[str]) -> bool:
        """Confirm booking of blocked seats"""
        for seat_id in seat_ids:
            seat = self.get_seat(seat_id)
            if not seat or not seat.book():
                return False
        return True

    def release_seats(self, seat_ids: List[str]):
        """Release seats back to available"""
        for seat_id in seat_ids:
            seat = self.get_seat(seat_id)
            if seat:
                seat.release()

    def calculate_total_amount(self, seat_ids: List[str]) -> float:
        """Calculate total price for given seats"""
        total = 0.0
        for seat_id in seat_ids:
            seat = self.get_seat(seat_id)
            if seat:
                total += seat.price
        return total

class Theater:
    def __init__(self, theater_id: str, name: str, location: str):
        self.theater_id = theater_id
        self.name = name
        self.location = location
        self.screens: Dict[str, Screen] = {}
        self.movies: Dict[str, Movie] = {}

    def add_screen(self, screen: Screen):
        self.screens[screen.screen_id] = screen

    def add_movie(self, movie: Movie):
        self.movies[movie.movie_id] = movie

    def create_show(self, movie_id: str, screen_id: str, start_time: datetime) -> Optional[Show]:
        movie = self.movies.get(movie_id)
        screen = self.screens.get(screen_id)
        
        if not movie or not screen:
            return None

        show_id = f"{movie_id}_{screen_id}_{start_time.strftime('%Y%m%d_%H%M')}"
        show = Show(show_id, movie, screen, start_time)
        screen.add_show(show)
        return show

    def find_show(self, show_id: str) -> Optional[Show]:
        """Find show across all screens in this theater"""
        for screen in self.screens.values():
            if show_id in screen.shows:
                return screen.shows[show_id]
        return None

    def get_shows_by_movie(self, movie_id: str) -> List[Show]:
        shows = []
        for screen in self.screens.values():
            for show in screen.shows.values():
                if show.movie.movie_id == movie_id:
                    shows.append(show)
        return shows

class Customer:
    def __init__(self, customer_id: str, name: str, email: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

    def get_customer_id(self):
        return self.customer_id
    
    def get_name(self):
        return self.name

# Factory Pattern
class TheaterFactory:
    @staticmethod
    def create_multiplex(theater_id: str, name: str, location: str, num_screens: int) -> Theater:
        theater = Theater(theater_id, name, location)
        for i in range(1, num_screens + 1):
            screen = Screen(f"S{i:03d}", f"Screen {i}", 60)
            theater.add_screen(screen)
        return theater

class BookingFactory:
    @staticmethod
    def create_booking(customer_id: str, show: Show, seat_ids: List[str], total_amount: float) -> Booking:
        booking_id = str(uuid.uuid4())
        return Booking(booking_id, customer_id, show, seat_ids, total_amount)

# Main System Class (Controller + Business Logic)
class BookingSystem:
    def __init__(self):
        self.theaters: Dict[str, Theater] = {}
        self.customers: Dict[str, Customer] = {}
        self.bookings: Dict[str, Booking] = {}

    def add_theater(self, theater: Theater):
        self.theaters[theater.theater_id] = theater

    def register_customer(self, customer: Customer):
        self.customers[customer.customer_id] = customer

    # Handle methods (Controller interface)
    def handle_booking_request(self, request: BookingRequest) -> bool:
        """Handle booking request"""
        return self._process_booking_request(request)

    def handle_cancellation_request(self, request: CancellationRequest) -> bool:
        """Handle cancellation request"""  
        return self._process_cancellation_request(request)

    def handle_availability_request(self, request: AvailabilityRequest):
        """Handle availability check request"""
        self._process_availability_request(request)

    # Internal processing methods
    def _process_availability_request(self, request: AvailabilityRequest):
        """Process seat availability check request"""
        show = self._find_show(request.get_show_id())
        if not show:
            request.available_seats = []
            request.total_available = 0
            return

        available_seats = show.screen.get_available_seats(request.get_seat_type())
        
        if request.get_seat_count():
            available_seats = available_seats[:request.get_seat_count()]
        
        request.available_seats = [seat.get_seat_id() for seat in available_seats]
        request.total_available = len(available_seats)

    def _process_booking_request(self, request: BookingRequest) -> bool:
        """Process booking request - main business logic here"""
        try:
            # Validate customer
            customer = self.customers.get(request.get_customer_id())
            if not customer:
                request.error_message = "Customer not found"
                return False

            # Find show
            show = self._find_show(request.get_show_id())
            if not show:
                request.error_message = "Show not found"
                return False

            # Check seat availability and block seats
            if not show.screen.block_seats(request.get_seat_ids()):
                request.error_message = "Selected seats are not available"
                return False

            # Calculate total amount
            total_amount = show.screen.calculate_total_amount(request.get_seat_ids())
            request.total_amount = total_amount

            # Process payment
            payment = Payment(str(uuid.uuid4()), total_amount, request.payment_method or "Credit Card")
            if not payment.process():
                show.screen.release_seats(request.get_seat_ids())
                request.error_message = "Payment failed"
                return False

            # Confirm booking
            if not show.screen.book_seats(request.get_seat_ids()):
                request.error_message = "Failed to confirm seat booking"
                return False

            # Create booking record
            booking = BookingFactory.create_booking(
                request.get_customer_id(), show, request.get_seat_ids(), total_amount
            )
            booking.set_payment(payment)
            self.bookings[booking.booking_id] = booking

            # Update request with results
            request.booking_id = booking.booking_id
            request.status = BookingStatus.CONFIRMED
            return True

        except Exception as e:
            request.error_message = f"Booking failed: {str(e)}"
            return False

    def _process_cancellation_request(self, request: CancellationRequest) -> bool:
        """Process booking cancellation request"""
        try:
            booking = self.bookings.get(request.get_booking_id())
            if not booking:
                request.error_message = "Booking not found"
                return False

            if booking.customer_id != request.get_customer_id():
                request.error_message = "Unauthorized cancellation attempt"
                return False

            if booking.status == BookingStatus.CANCELLED:
                request.error_message = "Booking already cancelled"
                return False

            # Release seats
            booking.show.screen.release_seats(booking.seat_ids)
            booking.status = BookingStatus.CANCELLED

            # Set refund amount (could have cancellation fees)
            request.refund_amount = booking.total_amount * 0.9  # 10% cancellation fee
            request.success = True
            return True

        except Exception as e:
            request.error_message = f"Cancellation failed: {str(e)}"
            return False

    def get_customer_bookings(self, customer_id: str) -> List[Booking]:
        """Get all bookings for a customer"""
        return [booking for booking in self.bookings.values() 
                if booking.customer_id == customer_id]

    def search_movies(self, location: str = None) -> List[Movie]:
        """Search movies by location"""
        movies = []
        for theater in self.theaters.values():
            if location is None or theater.location.lower() == location.lower():
                movies.extend(theater.movies.values())
        return list({movie.movie_id: movie for movie in movies}.values())  # Remove duplicates

    def get_shows(self, movie_id: str, date: datetime.date = None) -> List[Show]:
        """Get shows for a movie"""
        shows = []
        for theater in self.theaters.values():
            theater_shows = theater.get_shows_by_movie(movie_id)
            if date:
                theater_shows = [show for show in theater_shows 
                               if show.start_time.date() == date]
            shows.extend(theater_shows)
        return shows

    def _find_show(self, show_id: str) -> Optional[Show]:
        """Find show across all theaters"""
        for theater in self.theaters.values():
            show = theater.find_show(show_id)
            if show:
                return show
        return None



# Main Class (Following Elevator Pattern)
class Main:
    @staticmethod
    def main():
        print("=== Simple Movie Booking System Demo ===\n")
        
        # Initialize system (acts as controller)
        booking_system = BookingSystem()
        
        # Create theater using factory
        theater = TheaterFactory.create_multiplex("T001", "PVR Cinemas", "Mumbai", 2)
        
        # Add movie
        movie = Movie("M001", "Avengers: Endgame", 180, "Action")
        theater.add_movie(movie)
        
        # Create show
        show = theater.create_show("M001", "S001", datetime.now() + timedelta(hours=2))
        booking_system.add_theater(theater)
        
        # Register customer
        customer = Customer("C001", "John Doe", "john@email.com", "9876543210")
        booking_system.register_customer(customer)
        
        # 1. Check availability
        availability_request = AvailabilityRequest(show.show_id, 5, SeatType.PREMIUM)
        booking_system.handle_availability_request(availability_request)
        print(f"Available seats: {availability_request.available_seats}")
        
        # 2. Create booking request
        booking_request = BookingRequest("C001", show.show_id, ["A1", "A2", "A3"])
        booking_request.set_payment_method("Credit Card")
        
        # 3. Process booking
        success = booking_system.handle_booking_request(booking_request)
        
        if success:
            print(f"✅ Booking successful!")
            print(f"Booking ID: {booking_request.booking_id}")
            print(f"Total Amount: ₹{booking_request.total_amount}")
            print(f"Status: {booking_request.status.value}")
            
            # 4. Try to cancel booking
            cancellation_request = CancellationRequest(booking_request.booking_id, "C001")
            cancel_success = booking_system.handle_cancellation_request(cancellation_request)
            
            if cancel_success:
                print(f"✅ Cancellation successful!")
                print(f"Refund Amount: ₹{cancellation_request.refund_amount}")
            else:
                print(f"❌ Cancellation failed: {cancellation_request.error_message}")
                
        else:
            print(f"❌ Booking failed: {booking_request.error_message}")

# Demo Usage
def demo_simple_booking_system():
    Main.main()

if __name__ == "__main__":
    Main.main()