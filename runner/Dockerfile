FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs default-jdk-headless gcc g++ coreutils \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --uid 65534 --no-create-home --shell /usr/sbin/nologin runner
WORKDIR /work
USER 65534:65534
ENTRYPOINT ["python3", "/work/runner.py"]
