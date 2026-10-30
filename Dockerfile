FROM python:3.14.9-slim-bookworm@sha256:7dff173021016c8829ae58d5ce112ffc388073ebe67f351aeb6ba2909e35f847 AS builder

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /build
COPY requirements.txt .

RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt


FROM python:3.14.9-slim-bookworm@sha256:7dff173021016c8829ae58d5ce112ffc388073ebe67f351aeb6ba2909e35f847 AS runtime

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 \
       --create-home --home-dir /home/app \
       --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 src/ ./src/
COPY --chown=10001:10001 model.joblib ./model.joblib

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
