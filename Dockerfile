FROM python:3.8-slim
RUN apt-get update \
  && apt-get install -y --no-install-recommends git \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

# Install prepare_data package
# Create data volume
ENV DATA_PATH="/data"
RUN echo DATA_PATH=/data > .env
VOLUME /data

# Install backend
WORKDIR /backend
COPY ./requirements.txt /backend/requirements.txt
COPY ./pyproject.toml /backend/pyproject.toml

RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt
COPY ./app /backend/app

EXPOSE 80

# Set APP_VERSION
ARG APP_VERSION="0.0.1"
ENV APP_VERSION=${APP_VERSION}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
