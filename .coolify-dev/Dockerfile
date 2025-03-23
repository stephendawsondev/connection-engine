# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.13.0

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /connection_engine

RUN mkdir -p /var/log/django

# Copy the current directory contents into the container at /connection_engine
COPY . /connection_engine/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies if package.json exists
RUN if [ -f package.json ]; then npm install; fi

# Make port 3003 available to the world outside this container
EXPOSE 3003

# Run the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:3003", "--access-logfile", "-", "--error-logfile", "-", "connection_engine.wsgi:application"]
