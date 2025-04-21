from ninja import Schema
from typing import Optional






class CompanyIn(Schema):
    name: str
    description: Optional[str] = None


class CompanyOut(Schema):
    id: int
    name: str
    description: Optional[str]