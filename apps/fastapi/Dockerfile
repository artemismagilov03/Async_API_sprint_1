FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR code/
COPY . .
RUN pip --no-cache-dir install -r requirements.txt

# need changing after to ready prodaction on `run`
CMD ["fastapi", "dev", "src/main.py","--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
