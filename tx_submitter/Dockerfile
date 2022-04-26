FROM python:3.10.4-slim

COPY . /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r ./tx_submitter/requirements.txt

ENTRYPOINT python -m tx_submitter