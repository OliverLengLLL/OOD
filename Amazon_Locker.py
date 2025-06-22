#Deliver person need to put the package into locker
#People need to retreat the package from locker

#When Deliver person put a package into locker => a notification will send to the person which this package belonged to 
#That person who recieve the notification will use the code to open the locker
from enum import Enum
from datetime import datetime
import random
import string
from typing import Optional, Dict, List


class Size(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

    @staticmethod
    def get_larger_sizes(size):
        """Get a list of sizes equal to or larger than the given size"""
        if size == Size.SMALL:
            return [Size.SMALL, Size.MEDIUM, Size.LARGE]
        elif size == Size.MEDIUM:
            return [Size.MEDIUM, Size.LARGE]
        else:
            return [Size.LARGE]


class LockerStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


class Notification:
    @staticmethod
    def send(recipient_phone: str, message: str) -> None:
        # In a real system, this would send an SMS or other notification
        print(f"Notification sent to {recipient_phone}: {message}")


class Package:
    def __init__(self, package_id: str, recipient_name: str, recipient_phone: str, size: Size):
        self.package_id = package_id
        self.recipient_name = recipient_name
        self.recipient_phone = recipient_phone
        self.size = size


class Locker:
    def __init__(self, locker_id: str, size: Size):
        self.locker_id = locker_id
        self.size = size
        self.status = LockerStatus.AVAILABLE

    def mark_occupied(self) -> None:
        """Mark the locker as occupied"""
        self.status = LockerStatus.OCCUPIED

    def mark_available(self) -> None:
        """Mark the locker as available"""
        self.status = LockerStatus.AVAILABLE

    def is_available(self) -> bool:
        """Check if the locker is available"""
        return self.status == LockerStatus.AVAILABLE


class LockerSystem:
    def __init__(self):
        # Dictionary to store lockers
        self.lockers: Dict[str, Locker] = {}

        # Dictionary to track which package is in which locker
        self.locker_contents: Dict[str, Package] = {}

        # Dictionary to store access codes for lockers
        self.access_codes: Dict[str, str] = {}

    def add_locker(self, locker_id: str, size: Size) -> None:
        """Add a new locker to the system"""
        self.lockers[locker_id] = Locker(locker_id, size)

    def generate_access_code(self) -> str:
        """Generate a random 6-digit access code"""
        return ''.join(random.choices(string.digits, k=6))

    def find_available_locker_for_package(self, package_size: Size) -> Optional[Locker]:
        """Find an available locker for a package with the given size

        First tries to find a locker of the same size.
        If not available, tries larger sizes in ascending order.
        """
        compatible_sizes = Size.get_larger_sizes(package_size)

        for size in compatible_sizes:
            for locker in self.lockers.values():
                if locker.is_available() and locker.size == size:
                    return locker

        return None

    def deliver_package(self, package: Package) -> Optional[str]:
        """Deliver a package to an available locker of appropriate size"""
        # Find an appropriate locker
        locker = self.find_available_locker_for_package(package.size)
        if not locker:
            print(f"No available lockers for package size {package.size.value}")
            return None

        # Generate access code
        access_code = self.generate_access_code()

        # Store package in locker
        locker.mark_occupied()
        self.locker_contents[locker.locker_id] = package
        self.access_codes[locker.locker_id] = access_code

        # Send notification to recipient
        message = f"Your package {package.package_id} has been delivered. " \
                  f"Use code {access_code} to open locker {locker.locker_id}."
        Notification.send(package.recipient_phone, message)

        print(f"Package {package.package_id} ({package.size.value}) delivered to " 
              f"{locker.size.value} locker {locker.locker_id}")

        return locker.locker_id

    def retrieve_package(self, locker_id: str, access_code: str) -> Optional[Package]:
        """Retrieve a package from a locker"""
        # Check if locker exists
        if locker_id not in self.lockers:
            print(f"Locker {locker_id} not found")
            return None

        # Check if locker has a package
        if locker_id not in self.locker_contents:
            print(f"Locker {locker_id} is empty")
            return None

        # Verify access code
        if self.access_codes.get(locker_id) != access_code:
            print("Invalid access code")
            return None

        # Retrieve package
        package = self.locker_contents[locker_id]

        # Reset locker
        self.lockers[locker_id].mark_available()
        del self.locker_contents[locker_id]
        del self.access_codes[locker_id]

        print(f"Locker {locker_id} opened successfully")
        return package


# Example usage
def main():
    # Create locker system
    locker_system = LockerSystem()

    # Add lockers of different sizes
    locker_system.add_locker("S001", Size.SMALL)
    locker_system.add_locker("S002", Size.SMALL)
    locker_system.add_locker("M001", Size.MEDIUM)
    locker_system.add_locker("M002", Size.MEDIUM)
    locker_system.add_locker("L001", Size.LARGE)

    # Create packages of different sizes
    small_package = Package("PKG-S1", "John Doe", "555-1111", Size.SMALL)
    medium_package = Package("PKG-M1", "Jane Smith", "555-2222", Size.MEDIUM)
    large_package = Package("PKG-L1", "Bob Johnson", "555-3333", Size.LARGE)

    print("\n--- Package Delivery Tests ---")

    # Test 1: Deliver a small package (should use small locker)
    print("\nTest 1: Delivering small package")
    locker_id1 = locker_system.deliver_package(small_package)

    # Test 2: Deliver another small package (should use second small locker)
    print("\nTest 2: Delivering another small package")
    small_package2 = Package("PKG-S2", "Alice Brown", "555-4444", Size.SMALL)
    locker_id2 = locker_system.deliver_package(small_package2)

    # Test 3: Deliver a third small package (should use medium locker as small are full)
    print("\nTest 3: Delivering third small package when small lockers are full")
    small_package3 = Package("PKG-S3", "Charlie Green", "555-5555", Size.SMALL)
    locker_id3 = locker_system.deliver_package(small_package3)

    # Test 4: Deliver a medium package (should use remaining medium locker)
    print("\nTest 4: Delivering medium package")
    locker_id4 = locker_system.deliver_package(medium_package)

    # Test 5: Deliver another medium package (should use large locker as medium are full)
    print("\nTest 5: Delivering medium package when medium lockers are full")
    medium_package2 = Package("PKG-M2", "David White", "555-6666", Size.MEDIUM)
    locker_id5 = locker_system.deliver_package(medium_package2)

    # Test 6: Deliver a large package (should fail as all large lockers are full)
    print("\nTest 6: Delivering large package when no large lockers available")
    locker_id6 = locker_system.deliver_package(large_package)

    print("\n--- Package Retrieval Test ---")
    # Retrieve a package
    if locker_id1:
        access_code = locker_system.access_codes[locker_id1]
        print(f"Retrieving package from locker {locker_id1} with code {access_code}")
        retrieved_package = locker_system.retrieve_package(locker_id1, access_code)

        if retrieved_package:
            print(f"Package {retrieved_package.package_id} retrieved successfully")

        # Now try to deliver a large package (should now use the freed small locker)
        print("\nTest 7: Delivering small package after retrieval")
        new_small_package = Package("PKG-S4", "Eve Black", "555-7777", Size.SMALL)
        locker_system.deliver_package(new_small_package)


if __name__ == "__main__":
    main()