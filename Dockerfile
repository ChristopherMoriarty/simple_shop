FROM python:3.8-slim

WORKDIR /

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y netcat-traditional

COPY . .

WORKDIR /src

EXPOSE 8090

CMD ["uvicorn", "main:app", "--port", "8090"]