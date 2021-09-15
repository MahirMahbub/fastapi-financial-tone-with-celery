FROM python:3.8.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /srv/backend
WORKDIR /srv/backend
COPY requirements.txt /srv/backend/
RUN pip install --upgrade pip
RUN pip install torch==1.9.0+cpu torchvision==0.10.0+cpu torchaudio==0.9.0 torchtext==0.10.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install -r requirements.txt
#pip install --no-cache-dir -r requirements.txt
COPY . /srv/backend/
