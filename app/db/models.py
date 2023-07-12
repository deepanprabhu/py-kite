from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Request(Base):
    __tablename__ = "REQUEST_QUEUE"

    id = Column(Integer, primary_key=True, index=True)
    input = Column(Text)
    output = Column(Text)
    latency = Column(String(10))
    status = Column(String(30))
