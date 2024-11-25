#FROM python:latest
#WORKDIR /app
#COPY . /app
#COPY ./setup/requirements.txt /app
#RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
#CMD ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "80"]
##CMD ["python", "app.py"]

FROM python:latest

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
COPY ./setup/requirements.txt requirements.txt
COPY . /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

