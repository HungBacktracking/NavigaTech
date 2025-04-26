FROM python:3.13.2

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
