FROM python:3.9-slim
ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 5000
CMD python myapp.py

