from ninja import Schema
#from uuid import UUID


class UserOut(Schema):
    id: int
    username: str
    email: str
