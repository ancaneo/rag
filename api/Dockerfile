FROM python:alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk update
RUN apk add --no-cache g++

COPY app /app
WORKDIR app
RUN pip install --upgrade -r requirements.txt

CMD ["fastapi", "dev", "--host", "0.0.0.0", "main.py"]
