# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy only the necessary files to leverage Docker's cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Set PORT environment variable
ENV PORT=8080

# Set the entrypoint command to run the script
ENTRYPOINT ["python", "src/zwickfi/zwickfi.py"]
