from ninja import Schema
from datetime import datetime
from typing import Optional
from uuid import UUID
from client.schema import ClientOut
from servicetype.schema import ServiceTypeOut
from slot.schema import SlotOut


class BookingIn(Schema):
    slot_id: int
    service_type_id: int
    notes: Optional[str] = None

class BookingOut(Schema):
    id: int
    slot: SlotOut
    service_type: ServiceTypeOut
    client: ClientOut
    status: str
    created_at: datetime
    notes: Optional[str]

class BookingFilter(Schema):
    company_id: Optional[UUID] = None
    client_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None