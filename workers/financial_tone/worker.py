from io import BytesIO
from sys import exit
from time import sleep
from typing import (
    Any,
    Dict, List
)
from urllib import request
import traceback

from celery import Celery, states
from celery.exceptions import Ignore
from librosa import load, get_duration
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

from backend import (
    is_backend_running,
    get_backend_url
)

from broker import (
    is_broker_running,
    get_broker_url
)
def predictor(pipe_line, sentences):
  results = pipe_line(sentences)
  print(results)
  label_tag = {"LABEL_0": "neutral", "LABEL_1": "positive", "LABEL_2": "negative"}
  results = [{'label': label_tag[res["label"]], 'score': res["score"], "sentence": sentences[idx]} for idx, res in
             enumerate(results)]
  return results


def model_loader(load_model: str = 'yiyanghkust/finbert-tone', task_type:str = "sentiment-analysis"):
  import os
  print(os.getcwd())
  load_model = os.getcwd()+r"/model/finbert-tone/"
  finbert = BertForSequenceClassification.from_pretrained(load_model,num_labels=3)
  tokenizer = BertTokenizer.from_pretrained(load_model)
  nlp = pipeline(task_type, model=finbert, tokenizer=tokenizer)
  return nlp
if not is_backend_running():
    exit()

if not is_broker_running():
    exit()

financial_tone = Celery("finacial-tone", broker=get_broker_url(), backend=get_backend_url())
pipe_line = model_loader()

# @financial_tone.task(bind=True, name="financial-tone.test")
# def test(self, audio_url: str) -> List[int]:
#     print(audio_url)
#     for i in range(10):
#         import time
#         print(i)
#         time.sleep(1)
#     return [i for i in range(100)]

@financial_tone.task(bind=True, name="financial-tone.prediction")
def prediction_task(self, sentences):
    print(sentences)
    #
    # Object interface
    # #
    # splitter = SentenceSplitter(language='en')
    # splitted_sentences = splitter.split(text=sentences)
    # print("Splitted: ", splitted_sentences)
    # global pipe_line
    # if pipe_line is None:
    # pipe_line = model_loader()
    import os
    print(os.getcwd())
    load_model = os.getcwd() + r"/model/finbert-tone/"
    print(load_model)
    finbert = BertForSequenceClassification.from_pretrained(load_model, num_labels=3)
    tokenizer = BertTokenizer.from_pretrained(load_model)
    pipe_line = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)
    from nltk.tokenize import sent_tokenize
    import nltk
    text = "Good morning Dr. Adams. The patient is waiting for you in room number 3."
    nltk.download('punkt')
    sentences = sent_tokenize(sentences)
    results=None
    try:
        print("Starting Prediction....")
        results = pipe_line(sentences)
        print("Finished Prediction....")
        print(results)
        label_tag = {"LABEL_0": "neutral", "LABEL_1": "positive", "LABEL_2": "negative"}
        results = [{'label': label_tag[res["label"]], 'score': res["score"], "sentence": sentences[idx]} for idx, res in
                   enumerate(results)]
        # results = predictor(pipe_line, sentences)
    except Exception as e:
        print(e)
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
            negative_count += 1
            negative_prob += res['score']
        elif res['label'] == 'positive':
            neutral_flag = False
            positive_count += 1
            positive_prob += res['score']
        elif res['label'] == 'neutral':
            neutral_count += 1
            neutral_prob += res['score']
    if neutral_flag:
        return {
            # "paragraphSentimentScore": neutral_prob/neutral_count,
            "sentenceSentiment": results,
            "paragraphSentiment": {
                "label": "neutral",
                "score": neutral_prob / neutral_count
            }
        }
    else:
        neg_avg = negative_prob / negative_count if negative_count > 0 else 0.0
        pos_avg = positive_prob / positive_count if positive_count > 0 else 0.0
        neu_avg = neutral_prob / neutral_count if neutral_count > 0 else 0.0
        label = "negative" if neg_avg > pos_avg else "positive"
        print(neg_avg, pos_avg, neu_avg, neg_avg * pos_avg * neu_avg)
        score = 1
        score *= neg_avg if neg_avg > 0 else 1.0
        score *= pos_avg if pos_avg > 0 else 1.0
        score *= neu_avg if neu_avg > 0 else 1.0
        return {
            "sentenceSentiment": results,
            "paragraphSentiment": {
                "label": label,
                "score": score
            }
        }


'''
@audio.task(bind=True, name="financial-tone.audio_length")
def audio_length(self, audio_url: str) -> Dict[str, Any]:
    pass

    try:
        payload = request.urlopen(audio_url)
        data = payload.read()
    except Exception as e:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),  # info
                'traceback': traceback.format_exc().split('\n')
            }
        )
        raise Ignore()

    try:
        y, sr = load(BytesIO(data), sr=None)
    except Exception as e:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
                "message": "Unable to load file"
            }
        )
        raise Ignore()

    length = get_duration(y, sr)
    sleep(length / 10)  # Simulate a long task processing

    return {
        'audio_length': length
    }
'''
