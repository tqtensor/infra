FROM python:3.11-bullseye

RUN apt-get update && apt-get upgrade -y && apt-get clean

COPY predownload.py /ragflow/predownload.py

RUN pip install --upgrade pip && pip install huggingface-hub

ENTRYPOINT ["python", "/ragflow/predownload.py"]
