from ninja import Schema
from typing import Optional
from core.schemas import UserOut


class ClientIn(Schema):
    name: str
    phone: Optional[str] = None

class ClientOut(Schema):
    id: int
    name: str
    phone: Optional[str]
    user: UserOut