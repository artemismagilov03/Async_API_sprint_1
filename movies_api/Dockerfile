FROM python:alpine

ENV PYTHONUNBUFFERED 1

WORKDIR code/
COPY ./requirements.txt .
RUN pip --no-cache-dir install -r requirements.txt
COPY . .

# need changing after to ready prodaction on `run`
CMD ["fastapi", "dev", "movies_api/main.py", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
