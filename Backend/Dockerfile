FROM python:3.12-slim

WORKDIR /QuizAI/Backend

COPY requirments.txt .
RUN pip install -r requirments.txt


COPY . . 

RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN curl -Ls https://cli.doppler.com/install.sh | sh

EXPOSE 8000

CMD ["doppler", "run", "--", "python", "app.py"]
