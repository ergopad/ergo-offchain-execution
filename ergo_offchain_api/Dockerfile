FROM python:3.10.4-slim

COPY . /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r ./ergo_offchain_api/requirements.txt

CMD tail /dev/null -f