from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import crud
from db.database import SessionLocal, engine
from db.models import Request
from db.models import Base
import traceback, sys
import uvicorn
from db.database import get_db
from sqlalchemy.engine import Engine
import concurrent.futures
from sqlalchemy import event

Base.metadata.create_all(bind=engine)
# Dependency

class PushRequest(BaseModel):
    input: str

class PushResponse(BaseModel):
    id: str
class StatusResponse(BaseModel):
    status: str

class DataResponse(BaseModel):
    input: str | None
    output: str | None
    latency: str | None

class UpdateRequest(BaseModel):
    input: str | None
    output: str | None
    latency: str | None
    status: str | None

app = FastAPI()

@app.post("/push")
async def push(push_request: PushRequest, db: Session = Depends(get_db)):
    try:
        for i in range(1, 20):
            db_request = crud.create_request(db, Request(input=push_request.input, status='queued'))
        return PushResponse(id=db_request.id)
    except:
        traceback.print_exception(*sys.exc_info())

@app.get("/status/{model_id}")
async def status(model_id, db: Session = Depends(get_db)):
    db_request = crud.get_request(db, model_id)
    return StatusResponse(status=db_request.status)

@app.get("/data/{model_id}")
async def data(model_id, db: Session = Depends(get_db)):
    db_request = crud.get_request(db, model_id)
    return DataResponse(input=db_request.input, output=db_request.output, latency=db_request.latency)

@app.post("/update/{model_id}")
async def data(update_request: UpdateRequest, model_id, db: Session = Depends(get_db)):
    crud.update_request(db, model_id, update_request.input, update_request.output, update_request.latency, 'finished')
    return "done"

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=80)