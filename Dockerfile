FROM python:3.9.13
WORKDIR /app
COPY requirements.txt requirements.txt
COPY main.py main.py
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "main.py"]
