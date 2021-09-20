from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline


def predictor_fixed(pipe_line, sentences):
    results = pipe_line(sentences)
    print(results)
    label_tag = {"LABEL_0": "neutral", "LABEL_1": "positive", "LABEL_2": "negative"}
    results = [{'label': label_tag[res["label"]], 'score': res["score"], "sentence": sentences[idx]} for idx, res in
               enumerate(results)]
    print(results)
    return results


def predictor_all(pipe_line, sentences):
    results = pipe_line(sentences)
    print(results)
    label_tag = {"LABEL_0": "neutral", "LABEL_1": "positive", "LABEL_2": "negative"}
    # results = [{'label': label_tag[res["label"]], 'score': res["score"], "sentence": sentences[idx]} for results_in in
    #            results for idx, res in enumerate(results_in)]
    final_result = []
    for idx, sentence_result in enumerate(results):
        inner_list = []
        for result_points in sentence_result:
            inner_list.append({'label': label_tag[result_points["label"]], 'score': result_points["score"]})
        final_result.append({
            "sentence": sentences[idx],
            "results": inner_list
        })

    print(final_result)
    return final_result


def model_loader(load_model: str = 'yiyanghkust/finbert-tone', task_type: str = "sentiment-analysis"):
    import os
    print(os.getcwd())
    load_model = os.getcwd() + r"/workers/model/finbert-tone"
    finbert = BertForSequenceClassification.from_pretrained(load_model, num_labels=3)
    tokenizer = BertTokenizer.from_pretrained(load_model)
    nlp_fixed = pipeline(task_type, model=finbert, tokenizer=tokenizer)
    nlp_all = pipeline(task_type, model=finbert, tokenizer=tokenizer, return_all_scores=True)
    return nlp_fixed, nlp_all
