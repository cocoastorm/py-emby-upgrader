FROM ubuntu:latest

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get update && apt-get install -yqq \
  python3 \
  python3-pip \
  python3-apt \
  && pip3 install -r requirements.txt \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python3", "upgrader.py"]

