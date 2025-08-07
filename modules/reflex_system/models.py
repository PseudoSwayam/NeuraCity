from pydantic import BaseModel, Field

class LocationPayload(BaseModel):
    """Payload for security-related actions."""
    location: str = Field(..., min_length=3, description="The specific location for the security dispatch.")

class AnnouncementPayload(BaseModel):
    """Payload for campus-wide announcements."""
    message: str = Field(..., min_length=10, description="The content of the announcement.")

class NotificationPayload(BaseModel):
    """Payload for notifying department admins."""
    department: str = Field(..., min_length=2, description="The target department (e.g., IT, Facilities).")
    message: str = Field(..., min_length=5, description="The message to send to the department admin.")