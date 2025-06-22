import datetime
import math
from enum import Enum
from typing import List, Optional, Dict

class SpotType(Enum):
    REGULAR = "regular"
    ACCESSIBLE = "accessible" 
    EV = "ev"
    ACCESSIBLE_EV = "accessible_ev"  # Spots that are both accessible and have EV charging

class SpotSize(Enum):
    COMPACT = 1
    REGULAR = 2
    LARGE = 3

class VehicleType(Enum):
    REGULAR = "regular"
    ACCESSIBLE = "accessible"  # Vehicle that needs accessible spot
    EV = "ev"  # Electric vehicle
    ACCESSIBLE_EV = "accessible_ev"  # Electric vehicle that needs accessible spot

class ParkingSpot:
    def __init__(self, spot_id: int, spot_type: SpotType, spot_size: SpotSize):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.spot_size = spot_size
        self.is_occupied = False
        self.current_vehicle = None
    
    def can_accommodate(self, vehicle) -> bool:
        # Check size compatibility (vehicle size must be <= spot size)
        if vehicle.get_spot_size().value > self.spot_size.value:
            return False
        
        # Check type compatibility
        vehicle_type = vehicle.get_vehicle_type()
        
        if vehicle_type == VehicleType.ACCESSIBLE:
            return self.spot_type in [SpotType.ACCESSIBLE, SpotType.ACCESSIBLE_EV]
        elif vehicle_type == VehicleType.EV:
            return self.spot_type in [SpotType.EV, SpotType.ACCESSIBLE_EV, SpotType.REGULAR]
        elif vehicle_type == VehicleType.ACCESSIBLE_EV:
            return self.spot_type == SpotType.ACCESSIBLE_EV
        else:  # Regular vehicle
            return self.spot_type in [SpotType.REGULAR, SpotType.EV, SpotType.ACCESSIBLE, SpotType.ACCESSIBLE_EV]
    
    def park_vehicle(self, vehicle):
        if self.can_accommodate(vehicle) and not self.is_occupied:
            self.is_occupied = True
            self.current_vehicle = vehicle
            return True
        return False
    
    def remove_vehicle(self):
        self.is_occupied = False
        vehicle = self.current_vehicle
        self.current_vehicle = None
        return vehicle

class Vehicle:
    def __init__(self, spot_size: SpotSize, vehicle_type: VehicleType = VehicleType.REGULAR):
        self._spot_size = spot_size
        self._vehicle_type = vehicle_type
    
    def get_spot_size(self) -> SpotSize:
        return self._spot_size
    
    def get_vehicle_type(self) -> VehicleType:
        return self._vehicle_type

class CompactCar(Vehicle):
    def __init__(self, vehicle_type: VehicleType = VehicleType.REGULAR):
        super().__init__(SpotSize.COMPACT, vehicle_type)

class RegularCar(Vehicle):
    def __init__(self, vehicle_type: VehicleType = VehicleType.REGULAR):
        super().__init__(SpotSize.REGULAR, vehicle_type)
    
class LargeCar(Vehicle):
    def __init__(self, vehicle_type: VehicleType = VehicleType.REGULAR):
        super().__init__(SpotSize.LARGE, vehicle_type)

class Driver:
    def __init__(self, driver_id: int, vehicle: Vehicle):
        self._id = driver_id
        self._vehicle = vehicle
        self._payment = 0
    
    def get_id(self) -> int:
        return self._id
    
    def get_vehicle(self) -> Vehicle:
        return self._vehicle
    
    def charge(self, amount: float) -> None:
        self._payment = amount
    
    def get_payment(self) -> float:
        return self._payment

class ParkingFloor:
    def __init__(self, floor_id: int, spot_configurations: Dict[SpotType, Dict[SpotSize, int]]):
        """
        spot_configurations example:
        {
            SpotType.REGULAR: {SpotSize.COMPACT: 10, SpotSize.REGULAR: 20, SpotSize.LARGE: 5},
            SpotType.ACCESSIBLE: {SpotSize.COMPACT: 2, SpotSize.REGULAR: 3, SpotSize.LARGE: 1},
            SpotType.EV: {SpotSize.COMPACT: 5, SpotSize.REGULAR: 8, SpotSize.LARGE: 2}
        }
        """
        self.floor_id = floor_id
        self.spots: List[ParkingSpot] = []
        self.vehicle_to_spot: Dict[Vehicle, ParkingSpot] = {}
        
        spot_id = 0
        for spot_type, size_config in spot_configurations.items():
            for spot_size, count in size_config.items():
                for _ in range(count):
                    self.spots.append(ParkingSpot(spot_id, spot_type, spot_size))
                    spot_id += 1
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        # First, try to find the most specific spot type that matches
        compatible_spots = [spot for spot in self.spots 
                          if spot.can_accommodate(vehicle) and not spot.is_occupied]
        
        if not compatible_spots:
            return False
        
        # Prioritize spot assignment based on vehicle type
        vehicle_type = vehicle.get_vehicle_type()
        
        if vehicle_type == VehicleType.ACCESSIBLE_EV:
            # Prefer accessible EV spots first
            preferred_spots = [s for s in compatible_spots if s.spot_type == SpotType.ACCESSIBLE_EV]
        elif vehicle_type == VehicleType.ACCESSIBLE:
            # Prefer accessible spots first
            preferred_spots = [s for s in compatible_spots if s.spot_type == SpotType.ACCESSIBLE]
        elif vehicle_type == VehicleType.EV:
            # Prefer EV spots first
            preferred_spots = [s for s in compatible_spots if s.spot_type == SpotType.EV]
        else:
            # Regular vehicles prefer regular spots to leave special spots available
            preferred_spots = [s for s in compatible_spots if s.spot_type == SpotType.REGULAR]
        
        # Use preferred spots if available, otherwise use any compatible spot
        spots_to_try = preferred_spots if preferred_spots else compatible_spots
        
        # Find the smallest compatible spot to optimize space usage
        spots_to_try.sort(key=lambda x: x.spot_size.value)
        
        for spot in spots_to_try:
            if spot.park_vehicle(vehicle):
                self.vehicle_to_spot[vehicle] = spot
                return True
        
        return False
    
    def remove_vehicle(self, vehicle: Vehicle) -> bool:
        if vehicle not in self.vehicle_to_spot:
            return False
        
        spot = self.vehicle_to_spot[vehicle]
        spot.remove_vehicle()
        del self.vehicle_to_spot[vehicle]
        return True
    
    def get_available_spots_by_type(self) -> Dict[SpotType, int]:
        counts = {}
        for spot in self.spots:
            if not spot.is_occupied:
                counts[spot.spot_type] = counts.get(spot.spot_type, 0) + 1
        return counts
    
    def get_vehicle_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        return self.vehicle_to_spot.get(vehicle)

class ParkingGarage:
    def __init__(self, floors: List[ParkingFloor]):
        self._parking_floors = floors
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        for floor in self._parking_floors:
            if floor.park_vehicle(vehicle):
                return True
        return False
    
    def remove_vehicle(self, vehicle: Vehicle) -> bool:
        for floor in self._parking_floors:
            if floor.remove_vehicle(vehicle):
                return True
        return False
    
    def get_availability_summary(self) -> Dict[int, Dict[SpotType, int]]:
        summary = {}
        for floor in self._parking_floors:
            summary[floor.floor_id] = floor.get_available_spots_by_type()
        return summary

class ParkingSystem:
    def __init__(self, parking_garage: ParkingGarage, hourly_rates: Dict[VehicleType, float]):
        self._parking_garage = parking_garage
        self._hourly_rates = hourly_rates  # Different rates for different vehicle types
        self._time_parked: Dict[int, datetime.datetime] = {}
    
    def park_vehicle(self, driver: Driver) -> bool:
        driver_id = driver.get_id()
        vehicle = driver.get_vehicle()
        current_time = datetime.datetime.now()
        
        is_parked = self._parking_garage.park_vehicle(vehicle)
        if is_parked:
            self._time_parked[driver_id] = current_time
        return is_parked
    
    def remove_vehicle(self, driver: Driver) -> bool:
        driver_id = driver.get_id()
        if driver_id not in self._time_parked:
            return False
        
        vehicle = driver.get_vehicle()
        current_time = datetime.datetime.now()
        time_diff = current_time - self._time_parked[driver_id]
        hours_parked = math.ceil(time_diff.total_seconds() / 3600)  # Round up to nearest hour
        
        # Get rate based on vehicle type
        vehicle_type = vehicle.get_vehicle_type()
        hourly_rate = self._hourly_rates.get(vehicle_type, self._hourly_rates[VehicleType.REGULAR])
        
        charge_amount = hours_parked * hourly_rate
        driver.charge(charge_amount)
        del self._time_parked[driver_id]
        
        return self._parking_garage.remove_vehicle(vehicle)
    
    def get_availability_summary(self):
        return self._parking_garage.get_availability_summary()

# Example usage:
if __name__ == "__main__":
    # Create parking floor configuration
    floor_config = {
        SpotType.REGULAR: {SpotSize.COMPACT: 10, SpotSize.REGULAR: 15, SpotSize.LARGE: 5},
        SpotType.ACCESSIBLE: {SpotSize.COMPACT: 2, SpotSize.REGULAR: 3, SpotSize.LARGE: 1},
        SpotType.EV: {SpotSize.COMPACT: 3, SpotSize.REGULAR: 5, SpotSize.LARGE: 2},
        SpotType.ACCESSIBLE_EV: {SpotSize.REGULAR: 2}
    }
    
    # Create floors
    floors = [ParkingFloor(i, floor_config) for i in range(3)]
    garage = ParkingGarage(floors)
    
    # Different rates for different vehicle types
    rates = {
        VehicleType.REGULAR: 5.0,
        VehicleType.ACCESSIBLE: 4.0,  # Discounted rate
        VehicleType.EV: 6.0,          # Higher rate due to charging
        VehicleType.ACCESSIBLE_EV: 5.0
    }
    
    parking_system = ParkingSystem(garage, rates)
    
    # Create different types of vehicles and drivers
    regular_car = RegularCar(VehicleType.REGULAR)
    ev_car = RegularCar(VehicleType.EV)
    accessible_car = CompactCar(VehicleType.ACCESSIBLE)
    accessible_ev = RegularCar(VehicleType.ACCESSIBLE_EV)
    
    drivers = [
        Driver(1, regular_car),
        Driver(2, ev_car),
        Driver(3, accessible_car),
        Driver(4, accessible_ev)
    ]
    
    # Park vehicles
    for driver in drivers:
        success = parking_system.park_vehicle(driver)
        vehicle_type = driver.get_vehicle().get_vehicle_type()
        print(f"Driver {driver.get_id()} with {vehicle_type.value} vehicle: {'Parked' if success else 'Failed to park'}")
    
    # Check availability
    availability = parking_system.get_availability_summary()
    print("\nAvailability summary:")
    for floor_id, spots in availability.items():
        print(f"Floor {floor_id}: {spots}")