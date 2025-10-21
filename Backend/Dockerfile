FROM python:3.12-slim

WORKDIR /QuizAI/Backend

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY . .



EXPOSE 8000
CMD ["python", "app.py"]
