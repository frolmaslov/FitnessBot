from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import date
from database_pgs import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    weight = Column(Integer)
    weight_wished = Column(Integer)
    online = Column(Boolean, default=True)
    date = Column(String)

    def __repr__(self):
        return f"<User {self.name} telegram_id={self.telegram_id} weight={self.weight} weight_wished={self.weight_wished} online={self.online} date={self.date}>"



