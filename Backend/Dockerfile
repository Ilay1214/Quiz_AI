FROM python:3.12-slim

WORKDIR /QuizAI/Backend

COPY requirments.txt .
RUN pip install -r requirments.txt


COPY . . 

RUN apt-get update && sudo apt-get install -y curl ca-certificates
RUN curl -Ls https://cli.doppler.com/install.sh | sh
RUN doppler -v

EXPOSE 8000

CMD ["doppler", "run", "--", "python", "app.py"]
