FROM python:3.10-alpine
WORKDIR /app
COPY src/requirements.txt requirements.txt
COPY src/main.py main.py
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
