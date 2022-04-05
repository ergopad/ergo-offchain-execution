FROM python:3

COPY . /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r ./filter_validator/requirements.txt

ENTRYPOINT python -m filter_validator