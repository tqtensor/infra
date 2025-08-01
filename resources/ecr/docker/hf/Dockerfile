FROM python:3.11-bullseye

RUN apt-get update && apt-get upgrade -y && apt-get clean

COPY predownload.py /hf/predownload.py

RUN pip install --upgrade pip && pip install huggingface-hub

ENTRYPOINT ["python", "/hf/predownload.py"]
