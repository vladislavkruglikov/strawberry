FROM python:3.13-slim

WORKDIR /opt

ENV PYTHONUNBUFFERED=1

RUN apt update && apt install --yes curl

RUN pip install --upgrade pip

RUN pip install prometheus-client==0.21.1 openai==1.59.4 aiofiles==24.1.0 aioboto3==13.3.0 loguru==0.7.3 httpx==0.28.1

COPY ./strawberry /opt/strawberry

ENTRYPOINT ["python", "-m", "strawberry"]
