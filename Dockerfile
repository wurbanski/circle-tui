FROM python:3.7-alpine

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY *.py /app/

ENTRYPOINT ["python", "/app/main.py"]
CMD ["--help"]
