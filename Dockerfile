FROM python:3.13-slim

WORKDIR /opt

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN pip install prometheus-client==0.21.1 openai==1.59.4

COPY ./strawberry /opt/strawberry

ENTRYPOINT ["python", "-m", "strawberry"]
