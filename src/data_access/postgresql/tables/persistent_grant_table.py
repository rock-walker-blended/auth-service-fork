from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, DateTime, Text, PickleType, String
from sqlalchemy.sql import func

from .base import Base


class PersistentGrants(Base): 
    __tablename__ = "persistent_grants"

    key = Column(String, unique=True, nullabe=False)
    creation_time = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(PickleType)
    subject_id = Column(Integer)
    type = Column(Text)


    @property
    def expiration(self) -> datetime:
        return datetime(self.creation_time) + timedelta(seconds=999)

    def __str__(self) -> str:
        return self.__tablename__

