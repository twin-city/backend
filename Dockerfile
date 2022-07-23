FROM python:3.7-slim
RUN apt-get update \
  && apt-get install -y --no-install-recommends git \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

# Install prepare_data package
# Create data volume


WORKDIR /workspace
RUN git clone --branch v1.2 https://github.com/twin-city/prepare-data.git
WORKDIR /workspace/prepare-data
RUN pip install -r requirements.txt
RUN pip install -e .
RUN echo DATA_PATH=/data > .env
VOLUME /data

# Install backend
WORKDIR /backend
COPY ./requirements.txt /backend/requirements.txt
COPY ./pyproject.toml /backend/pyproject.toml

RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt
COPY ./app /backend/app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
