FROM golang:1.13 as builder
WORKDIR /app
COPY invoke.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -v -o server

FROM python:3.9
# USER root
WORKDIR /app
COPY --from=builder /app/server ./
COPY . /app
# RUN apt-get update && apt-get install -y make
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pandas

ENTRYPOINT "./server"
