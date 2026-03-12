# labs/web_dev/task-manager/Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y nodejs npm curl postgresql-client

WORKDIR /app

# Install Python requirements for the lab interface
RUN pip install flask requests sqlalchemy psycopg2-binary

# Copy the lab logic
COPY app.py .

# Expose ports: 5000 (Interface), 8000 (User's API), 3000 (User's Frontend)
EXPOSE 5000 8000 3000

CMD ["python", "app.py"]