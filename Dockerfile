# Use a base image
FROM python:3.11-slim

# Install system dependencies, including git
RUN apt-get update && apt-get install -y git && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Add src to Python path and run as module
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "-m", "zwickfi"]
