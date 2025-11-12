from pydantic import BaseModel
from typing import List, Optional

class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    notification_type: str  # e.g., 'email', 'sms'
    is_read: bool = False
    created_at: str  # ISO format date string
    updated_at: str  # ISO format date string

class EmailNotification(Notification):
    subject: str
    recipient_email: str

class SMSNotification(Notification):
    recipient_phone: str
    sms_provider: Optional[str] = None

class NotificationResponse(BaseModel):
    notifications: List[Notification]
    total_count: int