# syntax=docker/dockerfile:experimental
# -- Base Image --
# Installs application dependencies
FROM python:3.11.9 as base

ARG VERSION

ENV PYTHONUNBUFFERED 1
ENV VERSION=$VERSION

RUN apt update
RUN apt install -y libopenblas-dev
RUN pip install poetry \
 && poetry config virtualenvs.create false 
# Set up application environment
WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./README.md ./
RUN mkdir ./fastlane_bot && touch ./fastlane_bot/__init__.py
RUN poetry install --only main --no-interaction

# -- Test Image --
# Code to be mounted into /app
FROM base as test
RUN poetry install --no-interaction
COPY ./.env ./main.py ./run_blockchain_terraformer.py ./run_tests ./
COPY ./fastlane_bot ./fastlane_bot
COPY ./resources/NBTest ./resources/NBTest
ENTRYPOINT ["./run_tests"]

# -- Production Image --
# Runs the service
FROM base as prod
COPY ./.env ./main.py ./run_blockchain_terraformer.py ./
COPY ./fastlane_bot ./fastlane_bot
ENTRYPOINT ["python", "main.py"]
