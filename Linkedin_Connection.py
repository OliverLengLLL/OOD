from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class RequestStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    ACCEPTED = "accepted"


class Referrer:
    def __init__(self, name: str, linkedin_profile_url: str, email: str = None):
        self.referrer_id = str(uuid.uuid4())
        self.name = name
        self.linkedin_profile_url = linkedin_profile_url
        self.email = email

    def __str__(self):
        return f"Referrer: {self.name} ({self.linkedin_profile_url})"


class ConnectionNoteTemplate:
    def __init__(self, content: str):
        self.template_id = str(uuid.uuid4())
        self.content = content

    def fill_template(self, data: Dict[str, str]) -> str:
        """Fill template with provided data using placeholders."""
        filled_content = self.content
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            filled_content = filled_content.replace(placeholder, value)
        return filled_content


class ConnectionRequest:
    def __init__(self, referrer: Referrer, note: str):
        self.request_id = str(uuid.uuid4())
        self.referrer = referrer
        self.note = note
        self.status = RequestStatus.PENDING
        self.created_at = datetime.now()
        self.sent_at = None

    def send(self) -> bool:
        """Send the connection request to the referrer."""
        try:
            # In a real implementation, this would use LinkedIn API or similar
            print(f"Sending connection request to {self.referrer.name}...")
            print(f"Message: {self.note}")

            # Simulate successful sending
            self.status = RequestStatus.SENT
            self.sent_at = datetime.now()
            return True
        except Exception as e:
            self.status = RequestStatus.FAILED
            print(f"Failed to send request: {e}")
            return False


class BatchRequestSender:
    def __init__(self):
        self.requests = []

    def add_request(self, request: ConnectionRequest):
        self.requests.append(request)

    def add_requests(self, requests: List[ConnectionRequest]):
        self.requests.extend(requests)

    def send_all(self) -> Dict[str, int]:
        """Send all connection requests in batch."""
        results = {
            "total": len(self.requests),
            "sent": 0,
            "failed": 0
        }

        for request in self.requests:
            success = request.send()
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1

        return results


class User:
    def __init__(self, name: str, email: str):
        self.user_id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.referrers = []

    def add_referrer(self, referrer: Referrer):
        self.referrers.append(referrer)
        return referrer

    def remove_referrer(self, referrer_id: str) -> bool:
        for i, referrer in enumerate(self.referrers):
            if referrer.referrer_id == referrer_id:
                self.referrers.pop(i)
                return True
        return False

    def get_referrers(self) -> List[Referrer]:
        return self.referrers


class ReferralManager:
    def __init__(self, user: User):
        self.user = user
        self.templates = []
        self.batch_sender = BatchRequestSender()

    def add_template(self, template: ConnectionNoteTemplate):
        self.templates.append(template)
        return template

    def save_referrer(self, name: str, linkedin_profile_url: str, email: str = None) -> Referrer:
        """Create and save a new referrer."""
        referrer = Referrer(name, linkedin_profile_url, email)
        self.user.add_referrer(referrer)
        return referrer

    def compose_note_for_referrer(self, referrer: Referrer, template: ConnectionNoteTemplate) -> str:
        """Compose personalized note for a referrer using template."""
        data = {
            "referrer_name": referrer.name,
            "user_name": self.user.name,
            "date": datetime.now().strftime("%B %d, %Y")
        }
        return template.fill_template(data)

    def create_connection_request(self, referrer: Referrer, template: ConnectionNoteTemplate) -> ConnectionRequest:
        """Create a connection request for a referrer."""
        note = self.compose_note_for_referrer(referrer, template)
        return ConnectionRequest(referrer, note)

    def prepare_batch_requests(self, template: ConnectionNoteTemplate, referrers: List[Referrer] = None):
        """Prepare batch connection requests for referrers."""
        if referrers is None:
            referrers = self.user.get_referrers()

        for referrer in referrers:
            request = self.create_connection_request(referrer, template)
            self.batch_sender.add_request(request)

    def send_batch_requests(self) -> Dict[str, int]:
        """Send all prepared batch requests."""
        return self.batch_sender.send_all()


# Example usage
if __name__ == "__main__":
    # Create a user
    user = User("John Doe", "john.doe@example.com")

    # Create referral manager
    manager = ReferralManager(user)

    # Create a template
    template_content = """
    Hi {referrer_name},

    I noticed you work at {company} and I'm interested in the {position} role. 
    Would you be open to referring me for this position?

    Thanks,
    {user_name}
    """
    template = manager.add_template(ConnectionNoteTemplate(template_content))

    # Add referrers
    manager.save_referrer("Alice Smith", "linkedin.com/in/alicesmith", "alice@company.com")
    manager.save_referrer("Bob Johnson", "linkedin.com/in/bobjohnson", "bob@company.com")
    manager.save_referrer("Carol Williams", "linkedin.com/in/carolwilliams")

    # Prepare and send batch requests
    manager.prepare_batch_requests(template)
    results = manager.send_batch_requests()

    print(f"\nBatch request results: {results}")
