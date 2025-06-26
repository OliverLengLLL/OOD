from enum import Enum
from datetime import datetime, timedelta
import random
import string
from typing import Dict, List, Optional

class LockerStatus(Enum):
    FREE = 'free'
    OCCUPIED = 'occupied'
    BROKEN = 'broken'

class LockerSize(Enum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3

class PackageSize(Enum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3

class NotificationType(Enum):
    DELIVERY = 'delivery'
    PICKUP_REMINDER = 'pickup_reminder'
    PICKUP_CONFIRMATION = 'pickup_confirmation'

class Customer:
    def __init__(self, customer_id: str, name: str, email: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

class DeliveryMan:
    def __init__(self, delivery_id: str, name: str, company: str):
        self.delivery_id = delivery_id
        self.name = name
        self.company = company

class Package:
    def __init__(self, package_id: str, package_size: PackageSize, customer_id: str, tracking_number: str):
        self.package_id = package_id
        self.size = package_size
        self.customer_id = customer_id
        self.tracking_number = tracking_number
        self.delivery_time = None
        self.access_code = None
        self.expiry_time = None

class Notification:
    def __init__(self, notification_type: NotificationType, recipient_id: str, message: str, delivery_method: str):
        self.notification_type = notification_type
        self.recipient_id = recipient_id
        self.message = message
        self.delivery_method = delivery_method  
        self.timestamp = datetime.now()
        self.sent = False

class DeliverPackageRequest:
    def __init__(self, package: Package, delivery_man: DeliveryMan, locker_location: str):
        self.package = package
        self.delivery_man = delivery_man
        self.locker_location = locker_location
        self.timestamp = datetime.now()

class GetPackageRequest:
    def __init__(self, customer_id: str, access_code: str, locker_id: str):
        self.customer_id = customer_id
        self.access_code = access_code
        self.locker_id = locker_id
        self.timestamp = datetime.now()

class Locker:
    def __init__(self, locker_id: str, locker_size: LockerSize, location: str):
        self.locker_id = locker_id
        self.locker_size = locker_size
        self.location = location
        self.locker_status = LockerStatus.FREE
        self.current_package = None
        self.assigned_time = None

    def is_available(self) -> bool:
        return self.locker_status == LockerStatus.FREE
    
    def can_fit_package(self, package_size: PackageSize) -> bool:
        return self.locker_size >= package_size
    
    def assign_package(self, package: Package) -> None:
        if not self.is_available():
            raise Exception(f"Locker {self.locker_id} is not available")
        
        if not self.can_fit_package(package.size):
            raise Exception(f"Package size {package.size} doesn't fit in locker size {self.size}")
        
        self.current_package = package
        self.assigned_time = datetime.now()
        self.locker_status = LockerStatus.OCCUPIED

    def release_locker(self) -> Package:
        if self.status != LockerStatus.OCCUPIED:
            raise Exception(f"Locker {self.locker_id} is not occupied")
        

        package = self.current_package
        self.current_package = None
        self.assigned_time = None
        self.locker_status = LockerStatus.FREE

        return package

class LockerSystem:
    def __init__(self):
        self.lockers: Dict[str, Locker] = {} # locker_id -> Locker
        self.customers: Dict[str, Customer] = {}  # customer_id -> Customer
        self.packages: Dict[str, Package] = {}  # package_id -> Package
        self.access_codes: Dict[str, str] = {}  # access_code -> locker_id
        self.notifications: List[Notification] = []
        self.pickup_expiry_hours = 72

    def add_locker(self, locker: Locker):
        self.lockers[locker.locker_id] = locker
    
    def add_customer(self, customer: Customer):
        self.customers[customer.customer_id] = customer

    def handle_deliver_package(self, request: DeliverPackageRequest) -> Dict[str, str]:
        try:
            package = request.package
            available_locker = self._find_available_lockers(package.size, request.locker_location)

            if not available_locker:
                return {
                    "success": False,
                    "message": "No available locker found for the package size"
                }

            access_code = self._generate_access_code()

            available_locker.assign_package(package)
            package.access_code = access_code
            package.delivery_time = datetime.now()
            package.expiry_time = datetime.now() + timedelta(hours=self.pickup_expiry_hours)

            self.packages[package.package_id] = package
            self.access_codes[access_code] = available_locker.locker_id

            self._send_delivery_notification(package)

            return {
                "success": True,
                "message": "Package delivered successfully",
                "locker_id": available_locker.locker_id,
                "access_code": access_code,
                "expiry_time": request.package.expiry_time.isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Delivery failed: {str(e)}"
            }
        
    def handle_get_package(self, request: GetPackageRequest) -> Dict[str, str]:
        """Handle package pickup request"""
        try:
            # Validate access code
            if request.access_code not in self.access_codes:
                return {
                    "success": False,
                    "message": "Invalid access code"
                }

            expected_locker_id = self.access_codes[request.access_code]
            if expected_locker_id != request.locker_id:
                return {
                    "success": False,
                    "message": "Access code doesn't match the locker"
                }

            locker = self.lockers[request.locker_id]
            package = locker.current_package

            # Validate customer
            if package.customer_id != request.customer_id:
                return {
                    "success": False,
                    "message": "Package doesn't belong to this customer"
                }

            # Check if package hasn't expired
            if datetime.now() > package.expiry_time:
                return {
                    "success": False,
                    "message": "Package pickup time has expired"
                }

            # Release package from locker
            released_package = locker.release_package()
            
            # Clean up
            del self.access_codes[request.access_code]
            del self.packages[package.package_id]

            # Send pickup confirmation
            self._send_pickup_confirmation(released_package)

            return {
                "success": True,
                "message": "Package retrieved successfully",
                "package_id": released_package.package_id,
                "tracking_number": released_package.tracking_number
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Pickup failed: {str(e)}"
            }


    def _find_available_lockers(self, package_size: PackageSize, location: str) -> Optional[Locker]:
        available_lockers = [
            locker for locker in self.lockers.values()
            if locker.location == location and 
               locker.is_available() and 
               locker.can_fit_package(package_size)
        ]
        
        if not available_lockers:
            return None
        
        return min(available_lockers, key=lambda l: l.size.value)

    def _generate_access_code(self) -> str:
        """Generate a unique 6-digit access code"""
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            if code not in self.access_codes:
                return code
            
    def _send_delivery_notification(self, package: Package):
        customer = self.customers.get(package.customer_id)

        if customer:
            message = f"Your package {package.tracking_number} has been delivered to locker. Access code: {package.access_code}. Expires: {package.expiry_time.strftime('%Y-%m-%d %H:%M')}"

            notification = Notification(
                NotificationType.DELIVERY,
                customer.customer_id,
                message,
                "email"
            )

            self.notifications.append(notification)
            self._send_notification(notification, customer)

    def _send_pickup_confirmation(self, package: Package):
        """Send pickup confirmation to customer"""
        customer = self.customers.get(package.customer_id)
        if customer:
            message = f"Your package {package.tracking_number} has been successfully picked up."
            notification = Notification(
                NotificationType.PICKUP_CONFIRMATION,
                customer.customer_id,
                message,
                "email"
            )
            self.notifications.append(notification)
            self._send_notification(notification, customer)

    def _send_notification(self, notification: Notification, customer: Customer):
        """Actually send the notification (mock implementation)"""
        print(f"Sending {notification.notification_type.value} to {customer.email}: {notification.message}")
        notification.sent = True

    def get_locker_status(self, locker_id: str) -> Dict:
        """Get status of a specific locker"""
        if locker_id not in self.lockers:
            return {"error": "Locker not found"}
        
        locker = self.lockers[locker_id]
        return {
            "locker_id": locker.locker_id,
            "size": locker.locker_size.name,
            "status": locker.locker_status.value,
            "location": locker.location,
            "occupied_since": locker.assigned_time.isoformat() if locker.assigned_time else None,
            "package_id": locker.current_package.package_id if locker.current_package else None
        }

    def get_all_lockers_status(self, location: str = None) -> List[Dict]:
        """Get status of all lockers, optionally filtered by location"""
        lockers = self.lockers.values()
        if location:
            lockers = [l for l in lockers if l.location == location]
        
        return [self.get_locker_status(locker.locker_id) for locker in lockers]
    

if __name__ == "__main__":
    # Initialize the system
    locker_system = LockerSystem()
    
    # Add some lockers
    locker_system.add_locker(Locker("L001", LockerSize.SMALL, "Downtown"))
    locker_system.add_locker(Locker("L002", LockerSize.MEDIUM, "Downtown"))
    locker_system.add_locker(Locker("L003", LockerSize.BIG, "Downtown"))
    
    # Add a customer
    customer = Customer("C001", "John Doe", "john@email.com", "+1234567890")
    locker_system.add_customer(customer)
    
    # Create a package
    package = Package("P001", PackageSize.SMALL, "C001", "TRK123456")
    
    # Create delivery request
    delivery_man = DeliveryMan("D001", "Mike Wilson", "Amazon Logistics")
    delivery_request = DeliverPackageRequest(package, delivery_man, "Downtown")
    
    # Handle delivery
    delivery_result = locker_system.handle_deliver_package(delivery_request)
    print("Delivery Result:", delivery_result)
    
    # Create pickup request
    if delivery_result["success"]:
        pickup_request = GetPackageRequest("C001", delivery_result["access_code"], delivery_result["locker_id"])
        pickup_result = locker_system.handle_get_package(pickup_request)
        print("Pickup Result:", pickup_result)
    
    # Check locker status
    print("Locker Status:", locker_system.get_all_lockers_status("Downtown"))