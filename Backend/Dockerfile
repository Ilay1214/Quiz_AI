FROM python:3.12-slim

WORKDIR /QuizAI/Backend

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt


COPY . . 

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar gzip \
 && rm -rf /var/lib/apt/lists/*
RUN set -eux; \
    ARCH=$(uname -m); \
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then DOPPLER_ARCH=x86_64; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then DOPPLER_ARCH=aarch64; \
    else echo "Unsupported arch: $ARCH" && exit 1; fi; \
    curl -fsSL --retry 3 -o /tmp/doppler.tar.gz "https://cli.doppler.com/download/latest?os=linux&arch=${DOPPLER_ARCH}"; \
    tar -xzf /tmp/doppler.tar.gz -C /usr/local/bin; \
    rm -f /tmp/doppler.tar.gz; \
    doppler --version

EXPOSE 8000

CMD ["doppler", "run", "--", "python", "app.py"]
