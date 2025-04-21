from ninja import Schema
from typing import Optional


class UserCreateIn(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_company: bool = False
    is_client: bool = False
    company_name: Optional[str] = None
    client_name: Optional[str] = None
    phone: Optional[str] = None

class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]