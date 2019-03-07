FROM python:3.7-alpine

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY *.py /app/
COPY circle_tui /app/circle_tui

ENTRYPOINT ["python", "/app/circle-tui.py"]
CMD ["--help"]
