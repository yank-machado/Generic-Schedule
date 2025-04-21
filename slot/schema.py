from ninja import Schema
from datetime import datetime
from typing import Optional


class SlotIn(Schema):
    start_time: datetime  
    end_time: datetime
    

class SlotOut(Schema):
    id: int
    start_time: datetime
    end_time: datetime
    is_available: bool
    company_id: int


class SlotFilter(Schema):
    company_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    only_available: bool = True