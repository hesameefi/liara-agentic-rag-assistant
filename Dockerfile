FROM python:3.11-slim

WORKDIR /app

ENV PORT=3012

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3012

CMD ["python", "server.py"]
