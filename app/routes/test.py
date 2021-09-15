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
from app.custom_classes.finbert import model_loader,predictor

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
celery = Celery(broker=BROKER, backend=BACKEND)
#
# @api.get("/task")
# def get_task_result():
#     return "Hello"


class UrlItem(BaseModel):
    audio_url: str
    callback: bool = False

class Sentences(BaseModel):
    sentences: str
    callback: bool = False


TASKS = {
    'length': 'audio.audio_length',
    'results': 'euro.scrappy_result',
    'test': 'financial-tone.test',
    'prediction': 'financial-tone.prediction'
}

class TaskResult(BaseModel):
    id: str
    status: str
    error: Optional[str] = None
    result: Optional[Any] = None

def send_result(task_id):
    while True:
        result = celery.AsyncResult(task_id)
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
    def create__task(self, data: UrlItem, queue: BackgroundTasks):
        task = celery.send_task(
            name=TASKS['test'],
            kwargs={'audio_url': data.audio_url},
            queue='financial_tone'
        )
        if data.callback:
            queue.add_task(send_result, task.id)
        return {"id": task.id}

    @router.get("/celery-test")
    def get_task_result(self, task_id: str= Query(...)):
        result = celery.AsyncResult(task_id)

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

    @router.post("/prediction-task", status_code=HTTP_201_CREATED)
    def create_prediction_task(self, data: UrlItem, queue: BackgroundTasks):
        task = celery.send_task(
            name=TASKS['prediction'],
            kwargs={'sentences': data.audio_url},
            queue='financial_tone'
        )
        if data.callback:
            queue.add_task(send_result, task.id)
        return {"id": task.id}

    @router.get("/prediction-task")
    def get_pred_task_result(self, task_id: str= Query(...)):
        result = celery.AsyncResult(task_id)

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
    @router.get("/predict")
    def get_result(self, sentences: str = Query(...)):
        print(sentences)
        #
        # Object interface
        # #
        # splitter = SentenceSplitter(language='en')
        # splitted_sentences = splitter.split(text=sentences)
        # print("Splitted: ", splitted_sentences)
        from app.main import pipe_line
        if pipe_line is None:
            pipe_line = model_loader()
        from nltk.tokenize import sent_tokenize
        import nltk
        text = "Good morning Dr. Adams. The patient is waiting for you in room number 3."
        nltk.download('punkt')
        sentences= sent_tokenize(sentences)
        results = predictor(pipe_line, sentences)
        neutral_flag = True
        negative_count = 0
        negative_prob = 0
        positive_count = 0
        positive_prob = 0
        neutral_count = 0
        neutral_prob = 0
        for res in results:
            if res['label'] == 'negative':
                neutral_flag = False
                negative_count+=1
                negative_prob+=res['score']
            elif res['label'] == 'positive':
                neutral_flag = False
                positive_count+=1
                positive_prob+=res['score']
            elif res['label'] == 'neutral':
                neutral_count+=1
                neutral_prob += res['score']
        if neutral_flag:
            return {
                # "paragraphSentimentScore": neutral_prob/neutral_count,
                "sentenceSentiment": results,
                "paragraphSentiment": {
                    "label": "neutral",
                    "score": neutral_prob/neutral_count
                }
            }
        else:
            neg_avg = negative_prob/negative_count if negative_count > 0 else 0.0
            pos_avg = positive_prob/positive_count if positive_count > 0 else 0.0
            neu_avg = neutral_prob/neutral_count if neutral_count > 0 else 0.0
            label = "negative" if neg_avg > pos_avg else "positive"
            print(neg_avg, pos_avg, neu_avg, neg_avg*pos_avg*neu_avg)
            score = 1
            score *= neg_avg if neg_avg>0 else 1.0
            score *= pos_avg if pos_avg > 0 else 1.0
            score *= neu_avg if neu_avg > 0 else 1.0
            return {
                "sentenceSentiment": results,
                "paragraphSentiment": {
                    "label": label,
                    "score": score
                }
            }

        # print(results)
        # return results