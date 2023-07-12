from sqlalchemy.orm import Session
from . import models, schemas

def get_request(db: Session, id: int):
    return db.query(models.Request).filter(models.Request.id == id).first()

def create_request(db: Session, request: schemas.Request):
    db_request = models.Request(input=request.input, output=request.output, latency=request.latency, status=request.status)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def set_request_status(db: Session, id: int, status: str):
    db_request = get_request(id)
    db_request.status = status
    db.flush()
    db.commit()

def get_queued_request(db: Session):
    db.flush()
    return db.query(models.Request).filter(models.Request.status == "queued").first()

def update_request(db: Session, id, input, output, latency, status):
    try:
        req:models.Request = db.query(models.Request).filter(models.Request.id == id).first();
        req.input = input
        req.output = output
        req.status = status
        req.latency = latency
        db.flush()
        db.commit()
    except Exception as e:
        raise e