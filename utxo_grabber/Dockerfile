FROM python:3

COPY . /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r ./utxo_grabber/requirements.txt

ENTRYPOINT python -m utxo_grabber