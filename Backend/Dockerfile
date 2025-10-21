FROM python:3.12-slim

WORKDIR /QuizAI/Backend

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY . .

# Install Doppler via official apt repository
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL --retry 3 https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key | gpg --dearmor -o /etc/apt/keyrings/doppler.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/doppler.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" > /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends doppler && \
    rm -rf /var/lib/apt/lists/*

# Verify
RUN doppler --version

EXPOSE 8000
CMD ["doppler", "run", "--", "python", "app.py"]
