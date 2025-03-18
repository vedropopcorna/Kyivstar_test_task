# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional system dependencies if required
RUN apt-get update && \
    apt-get install -y g++ make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD . /app

# Expose port 8030 for the FastAPI app
EXPOSE 8030

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8030"]