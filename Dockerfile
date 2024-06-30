# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary dependencies
RUN pip install --no-cache-dir flask

# Make port 5000 available to the world outside this container
EXPOSE 48080

# Run the application
CMD ["python", "app.py"]

