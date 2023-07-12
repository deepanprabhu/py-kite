from pydantic import BaseModel

class Request(BaseModel):
    id: int
    input: str
    output: str
    latency: str
    status: str

    class Config:
        orm_mode = True
