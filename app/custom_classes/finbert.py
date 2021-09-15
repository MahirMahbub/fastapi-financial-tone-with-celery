from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

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
  load_model = os.getcwd()+r"/workers/model/finbert-tone/"
  finbert = BertForSequenceClassification.from_pretrained(load_model,num_labels=3)
  tokenizer = BertTokenizer.from_pretrained(load_model)
  nlp = pipeline(task_type, model=finbert, tokenizer=tokenizer)
  return nlp