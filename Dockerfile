FROM python:3.10-slim

COPY requirements.txt /

RUN pip install -r /requirements.txt \
	&& rm -rf /root/.cache

COPY src/ ./

ENV ENVIRONMENT_FILE=".env"

EXPOSE 8080

ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app:server"]
