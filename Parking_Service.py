from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid

class VehicleSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class Vehicle:
    def __init__(self, id: str, size: VehicleSize, license_plate: str) -> None:
        self._id = id
        self.size = size
        self.license_plate = license_plate
    
    def get_id(self) -> str:
        return self._id
    

class Driver:
    def __init__(self, id: str, vehicle: Vehicle, phone_num: str, name: str) -> None:
        self.id = id
        self.vehicle = vehicle
        self.phone_num = phone_num
        self.name = name

class SpotSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class SpotStatus(Enum):
    EMPTY = "empty"
    OCCUPIED = 'occupied'
    RESERVED = 'resvered'
    OUT_OF_SERVICE = 'out_of_service'

class ParkingSpot:
    def __init__(self, spot_id: str, size: SpotSize, level: int, spot_number:int) -> None:
        self.spot_id = spot_id
        self.size = size
        self.status = SpotStatus.EMPTY
        self.level = level
        self.spot_number = spot_number
        self.vehicle = None
        self.reserved_until = None

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        return self.size >= vehicle.size
    
    def is_available(self) -> bool:
        if self.satus == SpotStatus.EMPTY:
            return True

        if self.status == SpotStatus.RESERVED and self.reserved_until:
            # Check if reservation has expired
            if datetime.now() > self.reserved_until:
                self.status = SpotStatus.EMPTY
                self.reserved_until = None
                return True
        return False
    
    def reserve_spot(self, duration_minutes: int=15) -> bool:
        if self.is_available():
            self.status = SpotStatus.RESERVED
            self.reserved_until = datetime.now() + timedelta(minutes=duration_minutes)
            return True
        return False
    
    def occupy_spot(self, vehicle: Vehicle) -> bool:
        """Occupy spot with vehicle"""
        if self.is_available() or self.status == SpotStatus.RESERVED:
            self.status = SpotStatus.OCCUPIED
            self.vehicle = vehicle
            self.reserved_until = None
            return True
        return False
    
    def free_spot(self) -> bool:
        """Free the spot"""
        self.status = SpotStatus.EMPTY
        self.vehicle = None
        self.reserved_until = None
        return True

    
class ParkingLevel:
    def __init__(self, level: int, small_spots: int = 20, medium_spots: int = 20, large_spots: int = 10) -> None:
        self.level = level
        self.parking_spots: Dict[str, ParkingSpot] = {}
        self._initialize_spots(small_spots, medium_spots, large_spots)

    def _initialize_spots(self, small_spots: int, medium_spots: int, large_spots: int) -> None:
        """Initialize parking spots for this level"""
        spot_counter = 1
        
        # Create small spots
        for i in range(small_spots):
            spot_id = f"L{self.level}-S{spot_counter}"
            spot = ParkingSpot(spot_id, SpotSize.SMALL, self.level, spot_counter)
            self.parking_spots[spot_id] = spot
            spot_counter += 1
        
        # Create medium spots
        for i in range(medium_spots):
            spot_id = f"L{self.level}-M{spot_counter}"
            spot = ParkingSpot(spot_id, SpotSize.MEDIUM, self.level, spot_counter)
            self.parking_spots[spot_id] = spot
            spot_counter += 1
        
        # Create large spots
        for i in range(large_spots):
            spot_id = f"L{self.level}-L{spot_counter}"
            spot = ParkingSpot(spot_id, SpotSize.LARGE, self.level, spot_counter)
            self.parking_spots[spot_id] = spot
            spot_counter += 1

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find available spot that can fit the vehicle"""
        for spot in self.parking_spots.values():
            if spot.is_available() and spot.can_fit_vehicle(vehicle):
                return spot
        return None
    
    def get_available_spots_count(self) -> Dict[SpotSize, int]:
        """Get count of available spots by size"""
        count = {SpotSize.SMALL: 0, SpotSize.MEDIUM: 0, SpotSize.LARGE: 0}
        for spot in self.parking_spots.values():
            if spot.is_available():
                count[spot.size] += 1
        return count
    
class ParkingTicket:
    def __init__(self, ticket_id: str, vehicle: Vehicle, spot: ParkingSpot, entry_time: datetime) -> None:
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = entry_time
        self.exit_time = None
        self.amount_due = 0.0
        self.paid = False
    
    def calculate_parking_fee(self) -> float:
        """Calculate parking fee based on duration"""
        if not self.exit_time:
            self.exit_time = datetime.now()
        
        duration = self.exit_time - self.entry_time
        hours = duration.total_seconds() / 3600
        
        if hours < 2:
            return 5.0
        elif hours < 24:
            return 15.0
        elif hours < 72:  # 3 days
            return 25.0
        else:
            # Additional days beyond 3 days
            additional_days = int((hours - 72) / 24) + 1
            return 25.0 + (additional_days * 10.0)
        
class PaymentMethod(Enum):
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    CASH = 'cash'

class Payment:
    def __init__(self, payment_id: str, amount: float, method: PaymentMethod, card_number: str = None) -> None:
        self.payment_id = payment_id
        self.amount = amount
        self.method = method
        self.card_number = card_number[-4:] if card_number else None  # Store only last 4 digits
        self.timestamp = datetime.now()
        self.status = 'pending'
    
    def process_payment(self) -> bool:
        """Simulate payment processing"""
        # In real implementation, this would integrate with payment gateway
        if self.method == PaymentMethod.CREDIT_CARD and self.card_number:
            # Simulate credit card processing
            self.status = 'completed'
            return True
        elif self.method == PaymentMethod.CASH:
            self.status = 'completed'
            return True
        else:
            self.status = 'failed'
            return False
        
class ParkingGarage:
    def __init__(self, num_levels: int) -> None:
        self.parking_levels: Dict[int, ParkingLevel] = {}
        self.active_tickets: Dict[str, ParkingTicket] = {}
        self.completed_tickets: Dict[str, ParkingTicket] = {}
        
        # Initialize parking levels
        for level in range(1, num_levels + 1):
            self.parking_levels[level] = ParkingLevel(level)
    
    def get_total_capacity(self) -> Dict[SpotSize, int]:
        """Get total capacity by spot size"""
        total = {SpotSize.SMALL: 0, SpotSize.MEDIUM: 0, SpotSize.LARGE: 0}
        for level in self.parking_levels.values():
            for spot in level.parking_spots.values():
                total[spot.size] += 1
        return total
    
    def get_available_capacity(self) -> Dict[SpotSize, int]:
        """Get available capacity by spot size"""
        total = {SpotSize.SMALL: 0, SpotSize.MEDIUM: 0, SpotSize.LARGE: 0}
        for level in self.parking_levels.values():
            available = level.get_available_spots_count()
            for size, count in available.items():
                total[size] += count
        return total

class FindAvailableSpotRequest:
    def __init__(self, vehicle: Vehicle, preferred_level: Optional[int] = None) -> None:
        self.vehicle = vehicle
        self.preferred_level = preferred_level
        self.timestamp = datetime.now()

class ReserveSpotRequest:
    def __init__(self, vehicle: Vehicle, spot_id: str, duration_minutes: int = 15) -> None:
        self.vehicle = vehicle
        self.spot_id = spot_id
        self.duration_minutes = duration_minutes
        self.timestamp = datetime.now()

class ParkingRequest:
    def __init__(self, vehicle: Vehicle, driver: Driver, spot_id: Optional[str] = None) -> None:
        self.vehicle = vehicle
        self.driver = driver
        self.spot_id = spot_id  # If None, system will find available spot
        self.timestamp = datetime.now()

class PaymentRequest:
    def __init__(self, ticket_id: str, payment_method: PaymentMethod, card_number: str = None) -> None:
        self.ticket_id = ticket_id
        self.payment_method = payment_method
        self.card_number = card_number
        self.timestamp = datetime.now()

class ExitRequest:
    def __init__(self, ticket_id: str) -> None:
        self.ticket_id = ticket_id
        self.timestamp = datetime.now()


class ParkingService:
    def __init__(self, parking_garage: ParkingGarage) -> None:
        self.parking_garage = parking_garage
    
    def find_available_spot(self, request: FindAvailableSpotRequest) -> Optional[ParkingSpot]:
        """Find available parking spot for vehicle"""
        # If preferred level specified, check that level first
        if request.preferred_level and request.preferred_level in self.parking_garage.parking_levels:
            level = self.parking_garage.parking_levels[request.preferred_level]
            spot = level.find_available_spot(request.vehicle)
            if spot:
                return spot
        
        # Check all levels
        for level in self.parking_garage.parking_levels.values():
            spot = level.find_available_spot(request.vehicle)
            if spot:
                return spot
        
        return None
    
    def reserve_spot(self, request: ReserveSpotRequest) -> bool:
        """Reserve a specific parking spot"""
        # Find the spot
        for level in self.parking_garage.parking_levels.values():
            if request.spot_id in level.parking_spots:
                spot = level.parking_spots[request.spot_id]
                if spot.can_fit_vehicle(request.vehicle):
                    return spot.reserve_spot(request.duration_minutes)
        return False
    
    def park_vehicle(self, request: ParkingRequest) -> Optional[ParkingTicket]:
        """Park vehicle and generate ticket"""
        spot = None
        
        # If specific spot requested
        if request.spot_id:
            for level in self.parking_garage.parking_levels.values():
                if request.spot_id in level.parking_spots:
                    spot = level.parking_spots[request.spot_id]
                    break
        else:
            # Find available spot
            find_request = FindAvailableSpotRequest(request.vehicle)
            spot = self.find_available_spot(find_request)
        
        if spot and spot.can_fit_vehicle(request.vehicle):
            if spot.occupy_spot(request.vehicle):
                # Generate ticket
                ticket_id = str(uuid.uuid4())
                ticket = ParkingTicket(ticket_id, request.vehicle, spot, datetime.now())
                self.parking_garage.active_tickets[ticket_id] = ticket
                return ticket
        
        return None
    
    def calculate_fee(self, ticket_id: str) -> Optional[float]:
        """Calculate parking fee for ticket"""
        if ticket_id in self.parking_garage.active_tickets:
            ticket = self.parking_garage.active_tickets[ticket_id]
            fee = ticket.calculate_parking_fee()
            ticket.amount_due = fee
            return fee
        return None
    
    def process_payment(self, request: PaymentRequest) -> bool:
        """Process payment for parking ticket"""
        if request.ticket_id in self.parking_garage.active_tickets:
            ticket = self.parking_garage.active_tickets[request.ticket_id]
            
            # Calculate final fee
            final_fee = ticket.calculate_parking_fee()
            ticket.amount_due = final_fee
            
            # Process payment
            payment_id = str(uuid.uuid4())
            payment = Payment(payment_id, final_fee, request.payment_method, request.card_number)
            
            if payment.process_payment():
                ticket.paid = True
                return True
        
        return False
    
    def exit_vehicle(self, request: ExitRequest) -> bool:
        """Process vehicle exit"""
        if request.ticket_id in self.parking_garage.active_tickets:
            ticket = self.parking_garage.active_tickets[request.ticket_id]
            
            # Check if payment is completed
            if not ticket.paid:
                return False
            
            # Free the parking spot
            ticket.spot.free_spot()
            ticket.exit_time = datetime.now()
            
            # Move ticket to completed
            self.parking_garage.completed_tickets[request.ticket_id] = ticket
            del self.parking_garage.active_tickets[request.ticket_id]
            
            return True
        
        return False
    
    def get_parking_status(self) -> Dict:
        """Get current parking status"""
        available = self.parking_garage.get_available_capacity()
        total = self.parking_garage.get_total_capacity()
        
        return {
            'total_capacity': total,
            'available_capacity': available,
            'occupancy_rate': {
                size: round((total[size] - available[size]) / total[size] * 100, 2) if total[size] > 0 else 0
                for size in SpotSize
            },
            'active_tickets': len(self.parking_garage.active_tickets)
        }
    

# Example Usage
if __name__ == "__main__":
    # Create parking garage with 3 levels
    garage = ParkingGarage(3)
    parking_service = ParkingService(garage)
    
    # Create a vehicle and driver
    vehicle = Vehicle("V001", VehicleSize.MEDIUM, "ABC123")
    driver = Driver("D001", vehicle, "555-0123", "John Doe")
    
    # Park the vehicle
    park_request = ParkingRequest(vehicle, driver)
    ticket = parking_service.park_vehicle(park_request)
    
    if ticket:
        print(f"Vehicle parked successfully. Ticket ID: {ticket.ticket_id}")
        print(f"Spot: {ticket.spot.spot_id}")
        
        # Calculate fee (simulate some time passed)
        fee = parking_service.calculate_fee(ticket.ticket_id)
        print(f"Parking fee: ${fee}")
        
        # Process payment
        payment_request = PaymentRequest(ticket.ticket_id, PaymentMethod.CREDIT_CARD, "1234567890123456")
        payment_success = parking_service.process_payment(payment_request)
        
        if payment_success:
            print("Payment processed successfully")
            
            # Exit vehicle
            exit_request = ExitRequest(ticket.ticket_id)
            exit_success = parking_service.exit_vehicle(exit_request)
            
            if exit_success:
                print("Vehicle exited successfully")
            else:
                print("Exit failed")
        else:
            print("Payment failed")
    else:
        print("No available parking spots")
    
    # Check parking status
    status = parking_service.get_parking_status()
    print(f"Parking Status: {status}")