from abc import ABC, abstractmethod


class Coffee(ABC):

    @abstractmethod
    def get_description(self) -> str:
        pass
    

    @abstractmethod
    def get_cost(self) -> float:
        pass

class Expresso(Coffee):
    def get_description(self) -> str:
        return "Espresso"
    
    def get_cost(self):
        return 4.0
    

class Latte(Coffee):
    def get_description(self) -> str:
        return "Latte"
    
    def get_cost(self):
        return 5.6

class Cappuccino(Coffee):
    def get_description(self) -> str:
        return "Cappuccino"
    
    def get_cost(self):
        return 6.0
    
class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee

    def get_description(self):
        return self._coffee.get_description
    
    def get_cost(self):
        return self._coffee.get_cost()
    
class ExtraShot(CoffeeDecorator):
    def get_description(self):
        return f"{self._coffee.get_description()} + Extra Shot"
    
    def get_cost(self):
        return self._coffee.get_cost() + 10
    
class SoyMilk(CoffeeDecorator):
    """Replaces regular milk with soy milk"""
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} with Soy Milk"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 0.50

class VanillaSyrup(CoffeeDecorator):
    """Adds vanilla syrup"""
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + Vanilla Syrup"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 0.40

class LargeSize(CoffeeDecorator):
    """Makes the coffee large size"""
    
    def get_description(self) -> str:
        return f"Large {self._coffee.get_description()}"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() * 1.5
    
class MachineStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    BUSY = "busy"

@dataclass
class Order:
    order_id: str
    machine_id: str
    coffee_description: str
    cost: float
    timestamp: datetime
    processing_time: float = 0.0

@dataclass
class MachineStats:
    machine_id: str
    total_orders: int
    total_revenue: float
    average_processing_time: float
    status: MachineStatus

# ================ INDIVIDUAL COFFEE MACHINE ================

class CoffeeMachine:
    """Individual coffee machine"""
    
    def __init__(self, machine_id: str, location: str):
        self.machine_id = machine_id
        self.location = location
        self.status = MachineStatus.ONLINE
        self.orders: List[Order] = []
        self.total_revenue = 0.0
        self.maintenance_counter = 0
        self.max_orders_before_maintenance = 50
    
    def make_coffee(self, coffee: Coffee) -> Optional[Order]:
        """Make coffee and return order details"""
        if self.status != MachineStatus.ONLINE:
            return None
        
        # Simulate processing
        self.status = MachineStatus.BUSY
        processing_time = random.uniform(1.0, 3.0)  # Simulate brewing time
        
        order = Order(
            order_id=str(uuid.uuid4())[:8],
            machine_id=self.machine_id,
            coffee_description=coffee.get_description(),
            cost=coffee.get_cost(),
            timestamp=datetime.now(),
            processing_time=processing_time
        )
        
        self.orders.append(order)
        self.total_revenue += order.cost
        self.maintenance_counter += 1
        
        # Check if maintenance needed
        if self.maintenance_counter >= self.max_orders_before_maintenance:
            self.status = MachineStatus.MAINTENANCE
        else:
            self.status = MachineStatus.ONLINE
        
        return order
    
    def perform_maintenance(self):
        """Perform maintenance on the machine"""
        self.status = MachineStatus.MAINTENANCE
        self.maintenance_counter = 0
        # Simulate maintenance time
        self.status = MachineStatus.ONLINE
    
    def get_stats(self) -> MachineStats:
        """Get machine statistics"""
        avg_time = sum(o.processing_time for o in self.orders) / len(self.orders) if self.orders else 0
        return MachineStats(
            machine_id=self.machine_id,
            total_orders=len(self.orders),
            total_revenue=self.total_revenue,
            average_processing_time=avg_time,
            status=self.status
        )
    
    def is_available(self) -> bool:
        """Check if machine is available for orders"""
        return self.status == MachineStatus.ONLINE

# ================ COFFEE MAKER SERVICE ================

class CoffeeMakerService:
    """Service managing multiple coffee machines"""
    
    def __init__(self):
        self.machines: Dict[str, CoffeeMachine] = {}
        self.all_orders: List[Order] = []
    
    def add_machine(self, machine_id: str, location: str) -> bool:
        """Add a new coffee machine to the service"""
        if machine_id in self.machines:
            return False
        
        self.machines[machine_id] = CoffeeMachine(machine_id, location)
        print(f"✅ Added machine {machine_id} at {location}")
        return True
    
    def remove_machine(self, machine_id: str) -> bool:
        """Remove a coffee machine from service"""
        if machine_id in self.machines:
            del self.machines[machine_id]
            print(f"❌ Removed machine {machine_id}")
            return True
        return False
    
    def make_coffee(self, coffee: Coffee, preferred_machine_id: str = None) -> Optional[Order]:
        """Make coffee using available machines with load balancing"""
        
        # Try preferred machine first
        if preferred_machine_id and preferred_machine_id in self.machines:
            machine = self.machines[preferred_machine_id]
            if machine.is_available():
                order = machine.make_coffee(coffee)
                if order:
                    self.all_orders.append(order)
                    return order
        
        # Use load balancing - find least busy available machine
        available_machines = [m for m in self.machines.values() if m.is_available()]
        
        if not available_machines:
            return None  # No machines available
        
        # Simple load balancing: choose machine with fewest orders
        best_machine = min(available_machines, key=lambda m: len(m.orders))
        
        order = best_machine.make_coffee(coffee)
        if order:
            self.all_orders.append(order)
        
        return order
    
    def get_available_machines(self) -> List[str]:
        """Get list of available machine IDs"""
        return [mid for mid, machine in self.machines.items() if machine.is_available()]
    
    def get_machine_status(self, machine_id: str) -> Optional[MachineStats]:
        """Get status of specific machine"""
        if machine_id in self.machines:
            return self.machines[machine_id].get_stats()
        return None
    
    def get_service_stats(self) -> Dict:
        """Get overall service statistics"""
        total_orders = len(self.all_orders)
        total_revenue = sum(order.cost for order in self.all_orders)
        
        machine_stats = [machine.get_stats() for machine in self.machines.values()]
        
        online_machines = sum(1 for m in machine_stats if m.status == MachineStatus.ONLINE)
        maintenance_machines = sum(1 for m in machine_stats if m.status == MachineStatus.MAINTENANCE)
        
        return {
            "total_machines": len(self.machines),
            "online_machines": online_machines,
            "maintenance_machines": maintenance_machines,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": total_revenue / total_orders if total_orders > 0 else 0
        }
    
    def perform_maintenance(self, machine_id: str) -> bool:
        """Perform maintenance on specific machine"""
        if machine_id in self.machines:
            self.machines[machine_id].perform_maintenance()
            print(f"🔧 Performed maintenance on machine {machine_id}")
            return True
        return False
    
    def list_machines(self):
        """List all machines with their status"""
        print("\n=== Coffee Machine Fleet ===")
        for machine in self.machines.values():
            stats = machine.get_stats()
            print(f"🤖 {machine.machine_id} ({machine.location}): "
                  f"{stats.status.value} | Orders: {stats.total_orders} | "
                  f"Revenue: ${stats.total_revenue:.2f}")