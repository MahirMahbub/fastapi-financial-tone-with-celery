
FROM python:3.7-slim-buster

COPY requirements.txt /workers/requirements.txt

WORKDIR /workers

RUN apt-get update -yqq && \
    apt-get -yqq install libsndfile1 --no-install-recommends && \
    pip install  --upgrade pip && \
    pip install torch==1.9.0+cpu torchvision==0.10.0+cpu torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install  --compile -r requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

COPY . /workers

EXPOSE 6379 5672
