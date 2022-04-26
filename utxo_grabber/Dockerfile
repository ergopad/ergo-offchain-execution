FROM python:3.10.4-slim

COPY . /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get -y install g++ \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r ./utxo_grabber/requirements.txt

ENTRYPOINT python -m utxo_grabber