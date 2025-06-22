from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from enum import Enum
import uuid

class BookingStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELED = 'canclled'

class RoomType(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    CONFERENCE = 'conference'

class User:
    def __init__(self, user_id: str, name: str, email: str, phone: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.bookings: Set[str] = set()

    def add_booking(self, booking_id: str):
        self.bookings.add(booking_id)

    def remove_booking(self, booking_id: str):
        self.bookings.remove(booking_id)

class MeetingRoom:
    def __init__(self, room_id: str, name: str, capacity: int, room_type: RoomType, floor: int, amenities: List[str] = None):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
        self.floor = floor
        self.amenities = amenities or []
        self.bookings: Dict[str, 'Meeting'] = {}

    def is_available(self, start_time: datetime, end_time: datetime) -> bool:
        for booking_id, meeting in self.bookings.items():
            if meeting.status == BookingStatus.CONFIRMED and self._times_overlap(start_time, end_time, meeting.start_time, meeting.end_time):
                return False
        return True

    def _times_overlap(self, start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        return start1 < end2 and end1 > start2

    def add_booking(self, meeting):
        self.bookings[meeting.booking_id] = meeting

    def remove_booking(self, booking_id: str):
        if booking_id in self.bookings:
            del self.bookings[booking_id]


class Meeting:
    def __init__(self, meeting_room: MeetingRoom, user: User, start_time: datetime, end_time: datetime, attendees: List[User]=None):
        self.booking_id = str(uuid.uuid4())
        self.meeting_room = meeting_room
        self.organizer = user
        self.start_time = start_time
        self.end_time = end_time
        self.attendees = attendees or []
        self.status = BookingStatus.PENDING
        self.created_at = datetime.now()

    def get_duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def get_total_attendees(self) -> int:
        return len(self.attendees) + 1
    
    def confirm_booking(self):
        self.status = BookingStatus.CONFIRMED
    
    def cancel_booking(self):
        self.status = BookingStatus.CANCELLED

class BookingRequest:
    def __init__(self, user_id: str, title: str, start_time: datetime, 
                 end_time: datetime, attendee_count: int, room_type: RoomType = None,
                 amenities_required: List[str] = None, floor_preference: int = None):
        self.user_id = user_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.attendee_count = attendee_count
        self.room_type = room_type
        self.amenities_required = amenities_required or []
        self.floor_preference = floor_preference

class CancelRequest:
    def __init__(self, user_id: str, booking_id: str, reason: str = ""):
        self.user_id = user_id
        self.booking_id = booking_id
        self.reason = reason
        self.requested_at = datetime.now()

class SearchBookingRequest:
    def __init__(self, date: datetime.date = None, room_type: RoomType = None,
                 capacity_min: int = None, capacity_max: int = None,
                 floor: int = None, amenities: List[str] = None,
                 available_from: datetime = None, available_to: datetime = None):
        self.date = date or datetime.now().date()
        self.room_type = room_type
        self.capacity_min = capacity_min or 1
        self.capacity_max = capacity_max or 100
        self.floor = floor
        self.amenities = amenities or []
        self.available_from = available_from
        self.available_to = available_to

class BookingResponse:
    def __init__(self, success: bool, message: str, booking_id: str = None, 
                 meeting: Meeting = None):
        self.success = success
        self.message = message
        self.booking_id = booking_id
        self.meeting = meeting

class MeetingScheduleSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.meeting_rooms: Dict[str, MeetingRoom] = {}
        self.meetings: Dict[str, Meeting] = {}  # booking_id -> Meeting
        self._initialize_default_rooms()

    def _initialize_default_rooms(self):
        default_rooms = [
            MeetingRoom("room_001", "Conference Room A", 12, RoomType.CONFERENCE, 1, 
                       ["projector", "whiteboard", "video_conference"]),
            MeetingRoom("room_002", "Meeting Room B", 6, RoomType.MEDIUM, 1, 
                       ["whiteboard", "tv_screen"]),
            MeetingRoom("room_003", "Small Room C", 4, RoomType.SMALL, 2, 
                       ["whiteboard"]),
            MeetingRoom("room_004", "Large Room D", 15, RoomType.LARGE, 2, 
                       ["projector", "whiteboard", "video_conference", "catering"]),
        ]
        
        for room in default_rooms:
            self.meeting_rooms[room.room_id] = room

    def add_user(self, user: User):
        self.users[user.user_id] = user

    def add_room(self, meeting_room: MeetingRoom):
        self.meeting_rooms[meeting_room.room_id] = meeting_room

    def remove_room(self, meeting_room: MeetingRoom):
        if meeting_room.room_id in self.meeting_rooms:
            del self.meeting_rooms[meeting_room.room_id]

    def book_meeting(self, request: BookingRequest) -> BookingResponse:
        """Book a meeting room based on the request"""
        # Validate request
        errors = self._validate_booking_request(request)
        if errors:
            return BookingResponse(False, f"Validation errors: {', '.join(errors)}")
        
        # Check if user exists
        if request.user_id not in self.users:
            return BookingResponse(False, "User not found")
        
        user = self.users[request.user_id]
        
        # Find suitable room
        suitable_room = self._find_suitable_room(request)
        if not suitable_room:
            return BookingResponse(False, "No suitable room available for the requested time")
        
        # Create meeting
        meeting = Meeting(
            meeting_room=suitable_room,
            user=user,
            title=request.title,
            start_time=request.start_time,
            end_time=request.end_time
        )
        
        # Book the room
        meeting.confirm_booking()
        suitable_room.add_booking(meeting)
        user.add_booking(meeting.booking_id)
        self.meetings[meeting.booking_id] = meeting
        
        return BookingResponse(
            True, 
            f"Meeting booked successfully in {suitable_room.name}",
            meeting.booking_id,
            meeting
        )

    def cancel_booking(self, request: CancelRequest) -> BookingResponse:
        """Cancel a meeting booking"""
        # Validate request
        errors = self._validate_cancel_request(request)
        if errors:
            return BookingResponse(False, f"Validation errors: {', '.join(errors)}")
        
        # Check if booking exists
        if request.booking_id not in self.meetings:
            return BookingResponse(False, "Booking not found")
        
        meeting = self.meetings[request.booking_id]
        
        # Check if user can cancel (organizer only for simplicity)
        if meeting.organizer.user_id != request.user_id:
            return BookingResponse(False, "Only the meeting organizer can cancel")
        
        # Cancel the booking
        meeting.cancel_booking()
        meeting.meeting_room.remove_booking(request.booking_id)
        meeting.organizer.remove_booking(request.booking_id)
        
        return BookingResponse(
            True, 
            f"Meeting '{meeting.title}' cancelled successfully"
        )

    def search_available_rooms(self, request: SearchBookingRequest) -> List[MeetingRoom]:
        """Search for available meeting rooms based on criteria"""
        return self._find_suitable_room(request)

    def get_user_bookings(self, user_id: str) -> List[Meeting]:
        """Get all bookings for a specific user"""
        if user_id not in self.users:
            return []
        
        user_meetings = []
        for booking_id in self.users[user_id].bookings:
            if booking_id in self.meetings:
                user_meetings.append(self.meetings[booking_id])
        
        return sorted(user_meetings, key=lambda m: m.start_time)

    def get_room_schedule(self, room_id: str, date: datetime.date) -> List[Meeting]:
        """Get schedule for a specific room on a specific date"""
        if room_id not in self.meeting_rooms:
            return []
        
        return self.meeting_rooms[room_id].get_bookings_for_date(date)

    def _find_suitable_room(self, request: BookingRequest) -> Optional[MeetingRoom]:
        """Find the most suitable room for the booking request"""
        suitable_rooms = []
        
        for room in self.meeting_rooms.values():
            # Check capacity
            if room.capacity < request.attendee_count:
                continue
            
            # Check room type preference
            if request.room_type and room.room_type != request.room_type:
                continue
            
            # Check floor preference
            if request.floor_preference and room.floor != request.floor_preference:
                continue
            
            # Check amenities
            if request.amenities_required:
                if not all(amenity in room.amenities for amenity in request.amenities_required):
                    continue
            
            # Check availability
            if not room.is_available(request.start_time, request.end_time):
                continue
            
            suitable_rooms.append(room)
        
        if not suitable_rooms:
            return None
        
        # Return the smallest suitable room (optimize utilization)
        return min(suitable_rooms, key=lambda r: r.capacity)

    def _validate_booking_request(self, request: BookingRequest) -> List[str]:
        """Validate the booking request and return list of errors"""
        errors = []
        
        if not request.title or not request.title.strip():
            errors.append("Meeting title is required")
        
        if request.start_time >= request.end_time:
            errors.append("Start time must be before end time")
        
        if request.start_time < datetime.now():
            errors.append("Cannot book meetings in the past")
        
        if request.attendee_count <= 0:
            errors.append("Attendee count must be positive")
        
        duration = (request.end_time - request.start_time).total_seconds() / 60
        if duration < 15:
            errors.append("Meeting must be at least 15 minutes long")
        if duration > 480:  # 8 hours
            errors.append("Meeting cannot exceed 8 hours")
        
        return errors

    def _validate_cancel_request(self, request: CancelRequest) -> List[str]:
        """Validate the cancel request and return list of errors"""
        errors = []
        
        if not request.booking_id or not request.booking_id.strip():
            errors.append("Booking ID is required")
        
        if not request.user_id or not request.user_id.strip():
            errors.append("User ID is required")
        
        return errors




