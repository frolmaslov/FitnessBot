import string

from pydantic import BaseModel


class User(BaseModel):
    id: int
    telegram_id: int
    name: str
    weight_wished: int
    weight: int
    online: bool
    date: int
