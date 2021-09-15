from typing import (
    Any,
    Optional
)
from os import getenv

from celery import Celery, states
from fastapi import FastAPI, BackgroundTasks
from typing import Optional

from fastapi import FastAPI, Depends, Query, Path
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.depends.db_depend import get_db
from app.utils import catch_not_implemented_exception

app = FastAPI()
router = InferringRouter()

REDIS_HOST = getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = getenv("REDIS_PORT", "6379")
REDIS_PASS = getenv("REDIS_PASS", "password")
REDIS_DB = getenv("REDIS_DB_BACKEND", "0")

RABBITMQ_HOST = getenv("RABBITMQ_HOST", "127.0.0.1")
RABBITMQ_PORT = getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = getenv("RABBITMQ_PASS", "guest")
RABBITMQ_VHOST = getenv("RABBITMQ_VHOST", "")

# RabbitMQ connection string: amqp://user:pass@localhost:5672/myvhost
BROKER = "amqp://{userpass}{hostname}{port}{vhost}".format(
    hostname=RABBITMQ_HOST,
    userpass=RABBITMQ_USER + ":" + RABBITMQ_PASS + "@" if RABBITMQ_USER else "",
    port=":" + RABBITMQ_PORT if RABBITMQ_PORT else "",
    vhost="/" + RABBITMQ_VHOST if RABBITMQ_VHOST else ""
)

# Redis connection string: redis://user:pass@hostname:port/db_number
BACKEND = "redis://{password}{hostname}{port}{db}".format(
    hostname=REDIS_HOST,
    password=':' + REDIS_PASS + '@' if REDIS_PASS else '',
    port=":" + REDIS_PORT if REDIS_PORT else "",
    db="/" + REDIS_DB if REDIS_DB else ""
)

# api = FastAPI()
audio = Celery(broker=BROKER, backend=BACKEND)
#
# @api.get("/task")
# def get_task_result():
#     return "Hello"


class UrlItem(BaseModel):
    audio_url: str
    callback: bool = False


TASKS = {
    'length': 'audio.audio_length',
    'results': 'euro.scrappy_result',
    'test': 'financial-tone.test'
}

class TaskResult(BaseModel):
    id: str
    status: str
    error: Optional[str] = None
    result: Optional[Any] = None

def send_result(task_id):
    while True:
        result = audio.AsyncResult(task_id)
        if result.state in states.READY_STATES:
            break

    output = TaskResult(
        id=task_id,
        status=result.state,
        error=str(result.info) if result.failed() else None,
        result=result.get() if result.state == states.SUCCESS else None
    )

    print(output)  # Send result to somewhere
@cbv(router)
class Movies(object):
    db: Session = Depends(get_db)

    @router.get("/test")
    @catch_not_implemented_exception
    def get_test(self):
        return "Hello"

    @router.post("/celery-test", status_code=HTTP_201_CREATED)
    def create_audio_task(self, data: UrlItem, queue: BackgroundTasks):
        task = audio.send_task(
            name=TASKS['test'],
            kwargs={'audio_url': data.audio_url},
            queue='financial_tone'
        )
        if data.callback:
            queue.add_task(send_result, task.id)
        return {"id": task.id}

    @router.get("/celery-test")
    def get_task_result(self, task_id: str= Query(...)):
        result = audio.AsyncResult(task_id)

        output = TaskResult(
            id=task_id,
            status=result.state,
            error=str(result.info) if result.failed() else None,
            result=result.get() if result.state == states.SUCCESS else None
        )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content=output.dict()
        )