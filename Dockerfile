# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
# Uncomment the next line if you have a requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Run zwickfi.py when the container launches
CMD ["python3.11", "./src/zwickfi/zwickfi.py"]