from collections import deque
import heapq
import time
from enum import Enum

class State(Enum):
    IDLE = 1
    UP = 2
    DOWN = 3
    EMERGENCY = 4

class ElevatorType(Enum):
    PASSENGER = 1
    SERVICE = 2

class RequestOrigin(Enum):
    INSIDE = 1
    OUTSIDE = 2

class DoorState(Enum):
    OPEN = 1
    CLOSED = 2

class Request:
    def __init__(self, origin, origin_floor, destination_floor = None):
        self.origin = origin
        self.origin_floor = origin_floor 
        self.destination_floor = destination_floor

        self.direction = State.IDLE
        self.elevator_type = ElevatorType.PASSENGER

        if destination_floor is not None:
            if origin_floor > destination_floor:
                self.direction = State.DOWN
            elif origin_floor > destination_floor:
                self.direction = State.UP

    def get_origin_floor(self):
        return self.origin_floor
    
    def get_destination_floor(self):
        return self.destination_floor
    
    def get_origin(self):
        return self.origin

    def get_direction(self):
        return self.direction
    
    def __lt__(self, other):
        return self.destination_floor < other.destination_floor

class ServiceRequest(Request):
    def __init__(self, origin, current_floor=None, destination_floor=None):
        if current_floor is not None and destination_floor is not None:
            super().__init__(origin, current_floor, destination_floor)
        else:
            super().__init__(origin, destination_floor)

        self.elevator_type = ElevatorType.SERVICE

class Elevator:
    def __init__(self, current_floor, emergency_status):
        self.current_floor = current_floor
        self.state = State.IDLE
        self.emergency_status = emergency_status
        self.door_state = DoorState.CLOSED

    def open_doors(self):
        self.door_state = DoorState.OPEN
        print(f"Door is open on floor {self.current_floor}")

    def close_doors(self):
        self.door_state = DoorState.CLOSED
        print("The door is closed")

    def wait_for_seconds(self, seconds):
        time.sleep(seconds)

    def operate(self):
        pass

    def process_emergency(self):
        pass

    def get_current_floor(self):
        return self.current_floor

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def set_current_floor(self, floor):
        self.current_floor = floor

    def get_door_state(self):
        return self.door_state

    def set_emergency_status(self, status):
        self.emergency_status = status


class PassengerElevator(Elevator):
    def __init__(self, current_floor, emergency_status):
        super().__init__(current_floor, emergency_status)
        self.passenger_up_queue = []
        self.passenger_down_queue = []

    def operate(self):
        while self.passenger_up_queue or self.passenger_down_queue:
            self.process_requests()
        self.set_state(State.IDLE)
        print("All requests have been fulfilled, elevator is now", self.get_state())

    def process_emergency(self):
        self.passenger_up_queue.clear()
        self.passenger_down_queue.clear()
        self.set_current_floor(1)
        self.set_state(State.IDLE)
        self.open_doors()
        self.set_emergency_status(True)
        print("Queues cleared, current floor is",
              self.get_current_floor(), ". Doors are", self.get_door_state())
        
    def add_up_request(self, request):
        if request.get_origin() == RequestOrigin.OUTSIDE:
            pick_up_request = Request(request.get_origin(), request.get_origin_floor(), request.get_origin_floor())
            heapq.heappush(self.passenger_up_queue, pick_up_request)
        heapq.heappush(self.passenger_up_queue, request)

    def add_down_request(self, request):
        if request.get_origin() == RequestOrigin.OUTSIDE:
            pick_up_request = Request(request.get_origin(
            ), request.get_origin_floor(), request.get_origin_floor())
            heapq.heappush(self.passenger_down_queue, pick_up_request)
        heapq.heappush(self.passenger_down_queue, request)

    def process_up_requests(self):
        while self.passenger_up_queue:
            up_request = heapq.heappop(self.passenger_up_queue)

            if self.get_current_floor() == up_request.get_destination_floor():
                print("Currently on floor", self.get_current_floor(),
                      ". No movement as destination is the same.")
                continue
            print("The current floor is", self.get_current_floor(),
                  ". Next stop:", up_request.get_destination_floor())

            try:
                print("Moving ", end="")
                for _ in range(3):
                    print(".", end="", flush=True)
                    time.sleep(0.5)  # Pause for half a second between dots.
                time.sleep(1)  # Assuming 1 second to move to the next floor.
                print()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print("Error:", e)

            self.set_current_floor(up_request.get_destination_floor())
            print("Arrived at", self.get_current_floor())

            self.open_doors()
            # Simulating 3 seconds for people to enter/exit.
            self.wait_for_seconds(3)
            self.close_doors()

        print("Finished processing all the up requests.")

    def process_down_requests(self):
        while self.passenger_down_queue:
            down_request = heapq.heappop(self.passenger_down_queue)

            if self.get_current_floor() == down_request.get_destination_floor():
                print("Currently on floor", self.get_current_floor(),
                      ". No movement as destination is the same.")
                continue

            print("The current floor is", self.get_current_floor(),
                  ". Next stop:", down_request.get_destination_floor())

            try:
                print("Moving ", end="")
                for _ in range(3):
                    print(".", end="", flush=True)
                    time.sleep(0.5)  # Pause for half a second between dots.
                time.sleep(1)  # Assuming 1 second to move to the next floor.
                print()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print("Error:", e)

            self.set_current_floor(down_request.get_destination_floor())
            print("Arrived at", self.get_current_floor())

            self.open_doors()
            # Simulating 3 seconds for people to enter/exit.
            self.wait_for_seconds(3)
            self.close_doors()

        print("Finished processing all the down requests.")

    def process_requests(self):
        if self.get_state() == State.UP or self.get_state() == State.IDLE:
            self.process_up_requests()
            if self.passenger_down_queue:
                print("Now processing down requests...")
                self.process_down_requests()
        else:
            self.process_down_requests()
            if self.passenger_up_queue:
                print("Now processing up requests...")
                self.process_up_requests()


class ServiceElevator(Elevator):

    def __init__(self, current_floor, emergency_status):
        super().__init__(current_floor, emergency_status)
        self.service_queue = deque()

    def operate(self):
        while self.service_queue:
            curr_request = self.service_queue.popleft()

            print()  # Move to the next line after the dots.
            print("Currently at", self.get_current_floor())
            try:
                time.sleep(1)  # Assuming 1 second to move to the next floor.
                print(curr_request.get_direction(), end="")
                for _ in range(3):
                    print(".", end="", flush=True)
                    time.sleep(0.5)  # Pause for half a second between dots.
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print("Error:", e)

            self.set_current_floor(curr_request.get_destination_floor())
            self.set_state(curr_request.get_direction())
            print("Arrived at", self.get_current_floor())

            self.open_doors()
            # Simulating 3 seconds for loading/unloading.
            self.wait_for_seconds(3)
            self.close_doors()

        self.set_state(State.IDLE)
        print("All requests have been fulfilled, elevator is now", self.get_state())

    def add_request_to_queue(self, request):
        self.service_queue.append(request)

    def process_emergency(self):
        self.service_queue.clear()
        self.set_current_floor(1)
        self.set_state(State.IDLE)
        self.open_doors()
        self.set_emergency_status(True)
        print("Queue cleared, current floor is", self.get_current_floor(),
              ". Doors are", self.get_door_state())

class ElevatorFactory:
    @staticmethod
    def create_elevator(elevator_type: ElevatorType):
        if elevator_type == ElevatorType.PASSENGER:
            return PassengerElevator(1, False)
        elif elevator_type == ElevatorType.SERVICE:
            return ServiceElevator(1, False)
        else:
            return None
        
class Controller:

    def __init__(self, factory):
        self.factory = factory
        self.passenger_elevator = factory.create_elevator(ElevatorType.PASSENGER)
        self.service_elevator = factory.create_elevator(ElevatorType.SERVICE)

    def send_passenger_up_requests(self, request):
        self.passenger_elevator.add_up_request(request)

    def send_passenger_down_requests(self, request):
        self.passenger_elevator.add_down_request(request)

    def send_service_request(self, request):
        self.service_elevator.add_request_to_queue(request)

    def handle_passenger_requests(self):
        self.passenger_elevator.operate()

    def handle_service_requests(self):
        self.service_elevator.operate()

    def handle_emergency(self):
        self.passenger_elevator.process_emergency()
        self.service_elevator.process_emergency()

class Main:

    @staticmethod
    def main():
        factory = ElevatorFactory()
        controller = Controller(factory)

        controller.send_passenger_up_requests(
            Request(RequestOrigin.OUTSIDE, 1, 5)
        )
        controller.send_passenger_down_requests(
            Request(RequestOrigin.OUTSIDE, 4, 2)
        )
        controller.send_passenger_up_requests(
            Request(RequestOrigin.OUTSIDE, 3, 6)
        )
        controller.handle_passenger_requests()

        controller.send_passenger_up_requests(
            Request(RequestOrigin.OUTSIDE, 1, 9)
        )
        controller.send_passenger_down_requests(
            Request(RequestOrigin.INSIDE, 5))
        controller.send_passenger_up_requests(
            Request(RequestOrigin.OUTSIDE, 4, 12)
        )
        controller.send_passenger_down_requests(
            Request(RequestOrigin.OUTSIDE, 10, 2)
        )
        controller.handle_passenger_requests()

        print("Now processing service requests")

        controller.send_service_request(
            ServiceRequest(RequestOrigin.INSIDE, 13))
        controller.send_service_request(
            ServiceRequest(RequestOrigin.OUTSIDE, 13, 2)
        )
        controller.send_service_request(
            ServiceRequest(RequestOrigin.INSIDE, 13, 15)
        )

        controller.handle_service_requests()


if __name__ == "__main__":
    Main.main()


def _find_best_elevator(self, floor: int, request_direction: Direction) -> Elevator:
        """Find best elevator based on priority rules"""
        # Lists to categorize elevators by priority
        same_direction_elevators = []
        idle_elevators = []
        opposite_direction_elevators = []
        
        # Categorize each elevator
        for elevator in self.elevators:
            if elevator.state == ElevatorState.MAINTENANCE:
                continue
            
            # Check if elevator is moving in same direction as request
            if ((request_direction == Direction.UP and 
                 elevator.direction == Direction.UP and 
                 elevator.current_floor < floor) or
                (request_direction == Direction.DOWN and 
                 elevator.direction == Direction.DOWN and 
                 elevator.current_floor > floor)):
                same_direction_elevators.append(elevator)
            # Check if elevator is idle
            elif elevator.state == ElevatorState.IDLE:
                idle_elevators.append(elevator)
            # Must be moving in opposite direction
            else:
                opposite_direction_elevators.append(elevator)
        
        # Find nearest elevator in same direction
        best_elevator = self._find_nearest_elevator(same_direction_elevators, floor)
        
        # If no same-direction elevator, find nearest idle elevator
        if best_elevator is None:
            best_elevator = self._find_nearest_elevator(idle_elevators, floor)
        
        # If no idle elevator, find nearest opposite-direction elevator
        if best_elevator is None:
            best_elevator = self._find_nearest_elevator(opposite_direction_elevators, floor)
        
        return best_elevator
    
def _find_nearest_elevator(self, elevators: List[Elevator], floor: int) -> Optional[Elevator]:
    """Find nearest elevator from a list"""
    if not elevators:
        return None
    
    return min(elevators, key=lambda e: e.distance_to(floor))