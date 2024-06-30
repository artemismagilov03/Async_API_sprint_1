FROM python:alpine

ENV PYTHONUNBUFFERED 1

WORKDIR code/
COPY ./requirements.txt .
RUN pip --no-cache-dir install -r requirements.txt
COPY . .

# need changing after to ready prodaction on `run`
CMD ["gunicorn", "movies_api.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
EXPOSE 8000
