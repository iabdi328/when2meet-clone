# Use base image with SSL and build tools
FROM python:3.10

# Set working directory to inside flask_app
WORKDIR /app/flask_app

# Copy all files into container
COPY . /app

# Install required packages
RUN apt-get update && \
    apt-get install -y gcc libpq-dev build-essential libssl-dev libffi-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Run the app
CMD ["python", "app.py"]
