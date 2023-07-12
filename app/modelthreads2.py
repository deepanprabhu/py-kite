import threading
import logging
import uvicorn
from app.jobs.job_crud import *
import queue
from fastapi import FastAPI
from db.crud import *
from db.database import *
from db.models import Base
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
from collections import deque

Base.metadata.create_all(bind=engine)
app = FastAPI()

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )
BUF_SIZE = 10

MAC_SIZE = 15
job_machines = threading.Semaphore(MAC_SIZE)
m1 = deque(maxlen=MAC_SIZE)
ml = threading.Lock()
[m1.append(i) for i in range(MAC_SIZE)]

q = queue.Queue(BUF_SIZE)

def get_db():
    db:Session = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


class ProducerThread(threading.Thread):
    db:Session = None

    def __init__(self, db=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread, self).__init__()
        self.target = target
        self.name = name
        self.db:Session = SessionLocal()

    def run(self):
        while True:
            if not q.full():
                item:models.Request = get_queued_request(self.db)

                if item:
                    item.status='processing'
                    self.db.commit()
                    q.put(item.id, block=True)
                    logging.debug('Putting ' + str(item)
                                  + ' : ' + str(q.qsize()) + ' items in queue')
        return

config.load_incluster_config()
batch_v1 = client.BatchV1Api()

def spawn_job(item_id):
    try:
        db = SessionLocal()
        item:models.Request = get_request(db, item_id)
        if item:
            try:
                job_machines.acquire(blocking=True)

                job_id = None
                ml.acquire(blocking=True)
                job_id = m1.pop()
                ml.release()

                if job_id != None:
                    logging.debug("spawn_job acquired " + str(job_id) + "for row " + str(item.id))
                    job = create_model_job(job_id, item.input, "http://fastapi:80/update/"+str(item.id))

                    while True:
                        try:
                            logging.debug("spawn_job job spawning " + str(job_id) + "for row " + str(item.id))
                            create_job(batch_v1, job, job_id)
                            break
                        except:
                            logging.debug("spawn_job job spawning error " + str(job_id) + "for row " + str(item.id))
                            sleep(3)

                    logging.debug("spawn_job job active " + str(job_id) + "for row " + str(item.id))
                    delete_job(batch_v1, job_id)
                    logging.debug("spawn_job job deleted " + str(job_id) + "for row " + str(item.id))

                    ml.acquire(blocking=True)
                    m1.appendleft(job_id)
                    logging.debug("spawn_job machine returned " + str(job_id) + "for row " + str(item.id))
                    ml.release()

                job_machines.release()
                db.commit()
            except:
                db.commit()
                ml.release()
                job_machines.release()
                raise
    except Exception as e:
        logging.error("spawn_job Failure")
        logging.error(e)



@app.on_event("startup")
async def startup_event():
    db = None
    p = ProducerThread(name='producer', db=db)

    p.start()
    chunk = BUF_SIZE

    with ThreadPoolExecutor(max_workers=chunk, thread_name_prefix="worker") as e:
        while True:
            if not q.empty():
                item_id = q.get(block=True)
                logging.debug('ThreadPoolExecutor queue fetched ' + str(item_id))
                if item_id:
                    logging.debug('ThreadPoolExecutor submitting to node ' + str(item_id))
                    future = e.submit(spawn_job, item_id)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)